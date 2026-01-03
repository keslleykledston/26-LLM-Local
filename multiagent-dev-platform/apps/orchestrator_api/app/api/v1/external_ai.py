"""
External AI API endpoints - Controlled external AI usage
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from loguru import logger

from app.core.database import get_db
from app.models.external_ai_call import ExternalAICall
from app.services.external_ai_service import ExternalAIService

router = APIRouter()


# ━━━ Schemas ━━━
class ExternalAIRequest(BaseModel):
    """Schema for external AI request"""
    mission_id: int
    task_id: Optional[int] = None
    provider: str = Field(..., pattern="^(claude|openai|gemini|openrouter)$")
    purpose: str = Field(..., min_length=10)
    justification: str = Field(..., min_length=20)
    prompt: str = Field(..., min_length=10)
    require_approval: bool = True


class ExternalAIResponse(BaseModel):
    """Schema for external AI call response"""
    id: int
    provider: str
    purpose: str
    approved: bool
    response: Optional[dict]
    tokens_used: Optional[int]
    cost_usd: Optional[float]
    cached: bool

    class Config:
        from_attributes = True


# ━━━ Endpoints ━━━
@router.post("/request", response_model=ExternalAIResponse)
async def request_external_ai(
    request: ExternalAIRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request external AI usage

    This endpoint creates a request for external AI usage.
    If require_approval is True, it will wait for approval before executing.
    """
    try:
        # Create audit record
        ai_call = ExternalAICall(
            mission_id=request.mission_id,
            task_id=request.task_id,
            provider=request.provider,
            purpose=request.purpose,
            justification=request.justification,
            approved=not request.require_approval,
            request={"prompt": request.prompt},
        )
        db.add(ai_call)
        await db.commit()
        await db.refresh(ai_call)

        # If no approval required, execute immediately
        if not request.require_approval:
            external_ai_service = ExternalAIService()
            result = await external_ai_service.call_external_ai(ai_call.id, request.prompt)

            ai_call.response = result
            ai_call.tokens_used = result.get("tokens_used")
            ai_call.cost_usd = result.get("cost_usd")
            await db.commit()
            await db.refresh(ai_call)

        logger.info(
            f"🌐 External AI request: {request.provider} - {request.purpose} "
            f"(approved={ai_call.approved})"
        )

        return ai_call

    except Exception as e:
        logger.error(f"❌ Failed to request external AI: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls", response_model=List[ExternalAIResponse])
async def list_external_ai_calls(
    mission_id: Optional[int] = None,
    approved_only: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List external AI calls with optional filtering"""
    try:
        query = select(ExternalAICall).order_by(ExternalAICall.created_at.desc())

        if mission_id:
            query = query.where(ExternalAICall.mission_id == mission_id)

        if approved_only:
            query = query.where(ExternalAICall.approved == True)

        query = query.limit(limit)

        result = await db.execute(query)
        calls = result.scalars().all()

        return calls

    except Exception as e:
        logger.error(f"❌ Failed to list external AI calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calls/{call_id}/approve")
async def approve_external_ai_call(call_id: int, db: AsyncSession = Depends(get_db)):
    """Approve an external AI call and execute it"""
    try:
        result = await db.execute(select(ExternalAICall).where(ExternalAICall.id == call_id))
        ai_call = result.scalar_one_or_none()

        if not ai_call:
            raise HTTPException(status_code=404, detail="External AI call not found")

        if ai_call.approved:
            return {"message": "Already approved", "call_id": call_id}

        # Approve and execute
        ai_call.approved = True
        ai_call.approved_at = datetime.utcnow()
        ai_call.approved_by = "user"  # TODO: Get from auth context

        external_ai_service = ExternalAIService()
        prompt = ai_call.request.get("prompt", "")
        result = await external_ai_service.call_external_ai(call_id, prompt)

        ai_call.response = result
        ai_call.tokens_used = result.get("tokens_used")
        ai_call.cost_usd = result.get("cost_usd")

        await db.commit()

        logger.info(f"✅ Approved and executed external AI call #{call_id}")
        return {"message": "External AI call approved and executed", "call_id": call_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to approve external AI call: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_external_ai_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """Get external AI usage statistics"""
    try:
        since = datetime.utcnow() - timedelta(days=days)

        # Total calls
        total_result = await db.execute(
            select(func.count(ExternalAICall.id)).where(ExternalAICall.created_at >= since)
        )
        total_calls = total_result.scalar()

        # Approved calls
        approved_result = await db.execute(
            select(func.count(ExternalAICall.id)).where(
                and_(ExternalAICall.created_at >= since, ExternalAICall.approved == True)
            )
        )
        approved_calls = approved_result.scalar()

        # Total cost
        cost_result = await db.execute(
            select(func.sum(ExternalAICall.cost_usd)).where(
                and_(ExternalAICall.created_at >= since, ExternalAICall.approved == True)
            )
        )
        total_cost = cost_result.scalar() or 0.0

        # By provider
        provider_result = await db.execute(
            select(ExternalAICall.provider, func.count(ExternalAICall.id))
            .where(ExternalAICall.created_at >= since)
            .group_by(ExternalAICall.provider)
        )
        by_provider = {row[0]: row[1] for row in provider_result}

        return {
            "period_days": days,
            "total_calls": total_calls,
            "approved_calls": approved_calls,
            "total_cost_usd": float(total_cost),
            "by_provider": by_provider,
        }

    except Exception as e:
        logger.error(f"❌ Failed to get external AI stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
