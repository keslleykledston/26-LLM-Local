"""
Missions API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, AsyncGenerator
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import json
from loguru import logger

from app.core.database import get_db
from app.models.mission import Mission
from app.models.task import Task
from app.core.orchestrator import Orchestrator

router = APIRouter()


# ━━━ Schemas ━━━
class MissionCreate(BaseModel):
    """Schema for creating a mission"""
    title: str = Field(..., min_length=3, max_length=500)
    description: str = Field(..., min_length=10)
    created_by: Optional[str] = "user"
    metadata: Optional[dict] = {}


class MissionResponse(BaseModel):
    """Schema for mission response"""
    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    created_by: Optional[str]
    plan: Optional[dict]
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    mission_id: int
    agent_type: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[dict]
    error: Optional[str]

    class Config:
        from_attributes = True


# ━━━ Endpoints ━━━
@router.post("/", response_model=MissionResponse, status_code=201)
async def create_mission(
    mission_data: MissionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new development mission

    The orchestrator will:
    1. PLAN: Break down the mission into tasks
    2. EXECUTE: Delegate to specialized agents
    3. VALIDATE: Run lint, tests, build
    4. INTEGRATE: Create commits, update docs
    5. MEMORY: Update RAG knowledge base
    """
    try:
        # Create mission record
        mission = Mission(
            title=mission_data.title,
            description=mission_data.description,
            status="planning",
            created_by=mission_data.created_by,
            metadata=mission_data.metadata,
        )
        db.add(mission)
        await db.commit()
        await db.refresh(mission)

        logger.info(f"✅ Created mission #{mission.id}: {mission.title}")

        # Start orchestrator in background
        background_tasks.add_task(run_orchestrator, mission.id)

        return mission

    except Exception as e:
        logger.error(f"❌ Failed to create mission: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[MissionResponse])
async def list_missions(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List missions with optional filtering"""
    try:
        query = select(Mission).order_by(desc(Mission.created_at))

        if status:
            statuses = [value.strip() for value in status.split(",") if value.strip()]
            if len(statuses) == 1:
                query = query.where(Mission.status == statuses[0])
            else:
                query = query.where(Mission.status.in_(statuses))

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        missions = result.scalars().all()

        return missions

    except Exception as e:
        logger.error(f"❌ Failed to list missions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream", response_class=StreamingResponse)
async def stream_missions():
    """
    Stream mission updates via Server-Sent Events (SSE)

    This endpoint sends real-time updates about all missions,
    eliminating the need for polling.
    """
    from app.core.database import AsyncSessionLocal

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for mission updates"""
        last_update = datetime.utcnow()

        while True:
            try:
                # Create a new session for each query to avoid transaction issues
                async with AsyncSessionLocal() as db:
                    # Get missions updated since last check
                    result = await db.execute(
                        select(Mission)
                        .where(Mission.updated_at >= last_update)
                        .order_by(desc(Mission.updated_at))
                        .limit(50)
                    )
                    missions = result.scalars().all()

                    if missions:
                        # Update timestamp
                        last_update = max(m.updated_at for m in missions)

                        # Send updates
                        for mission in missions:
                            data = {
                                "id": mission.id,
                                "title": mission.title,
                                "description": mission.description,
                                "status": mission.status,
                                "created_at": mission.created_at.isoformat(),
                                "updated_at": mission.updated_at.isoformat(),
                                "completed_at": mission.completed_at.isoformat() if mission.completed_at else None,
                            }
                            yield f"data: {json.dumps(data)}\n\n"

                # Send heartbeat every 15 seconds
                yield f": heartbeat\n\n"

                # Wait before next check (reduce DB load)
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Get mission by ID"""
    try:
        result = await db.execute(select(Mission).where(Mission.id == mission_id))
        mission = result.scalar_one_or_none()

        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        return mission

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mission_id}/tasks", response_model=List[TaskResponse])
async def get_mission_tasks(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Get all tasks for a mission"""
    try:
        result = await db.execute(
            select(Task).where(Task.mission_id == mission_id).order_by(Task.created_at)
        )
        tasks = result.scalars().all()

        return tasks

    except Exception as e:
        logger.error(f"❌ Failed to get mission tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{mission_id}/cancel")
async def cancel_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Cancel a running mission"""
    try:
        result = await db.execute(select(Mission).where(Mission.id == mission_id))
        mission = result.scalar_one_or_none()

        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        if mission.status in ["completed", "failed", "cancelled"]:
            raise HTTPException(status_code=400, detail=f"Mission already {mission.status}")

        mission.status = "cancelled"
        mission.completed_at = datetime.utcnow()
        await db.commit()

        logger.info(f"❌ Cancelled mission #{mission_id}")

        return {"message": "Mission cancelled", "mission_id": mission_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cancel mission: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ━━━ Background Task ━━━
async def run_orchestrator(mission_id: int):
    """Run the orchestrator for a mission"""
    try:
        logger.info(f"🤖 Starting orchestrator for mission #{mission_id}")
        orchestrator = Orchestrator()
        await orchestrator.execute_mission(mission_id)
        logger.success(f"✅ Orchestrator completed mission #{mission_id}")
    except Exception as e:
        logger.error(f"❌ Orchestrator failed for mission #{mission_id}: {e}", exc_info=True)
