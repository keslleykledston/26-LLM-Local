"""
Memory API endpoints - RAG knowledge base management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from app.core.database import get_db
from app.models.memory_item import MemoryItem
from app.services.memory_service import MemoryService

router = APIRouter()


# ━━━ Schemas ━━━
class MemoryItemCreate(BaseModel):
    """Schema for creating memory item"""
    type: str = Field(..., pattern="^(adr|playbook|snippet|glossary)$")
    title: str = Field(..., min_length=3, max_length=500)
    content: str = Field(..., min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    approved: bool = False
    metadata: Optional[dict] = {}


class MemoryItemResponse(BaseModel):
    """Schema for memory item response"""
    id: int
    type: str
    title: str
    content: str
    category: Optional[str]
    tags: Optional[List[str]]
    vector_id: Optional[str]
    approved: bool

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Schema for RAG search"""
    query: str = Field(..., min_length=3)
    limit: int = Field(default=5, ge=1, le=20)
    type: Optional[str] = None


# ━━━ Endpoints ━━━
@router.post("/", response_model=MemoryItemResponse, status_code=201)
async def create_memory_item(
    item_data: MemoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new memory item and optionally embed it in Qdrant"""
    try:
        memory_item = MemoryItem(**item_data.model_dump())
        db.add(memory_item)
        await db.commit()
        await db.refresh(memory_item)

        # If approved, embed in Qdrant
        if memory_item.approved:
            memory_service = MemoryService()
            vector_id = await memory_service.embed_memory_item(memory_item)
            memory_item.vector_id = vector_id
            await db.commit()
            await db.refresh(memory_item)

        logger.info(f"✅ Created memory item: {memory_item.type}/{memory_item.title}")
        return memory_item

    except Exception as e:
        logger.error(f"❌ Failed to create memory item: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[MemoryItemResponse])
async def list_memory_items(
    type: Optional[str] = None,
    approved_only: bool = True,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List memory items"""
    try:
        query = select(MemoryItem)

        if type:
            query = query.where(MemoryItem.type == type)

        if approved_only:
            query = query.where(MemoryItem.approved == True)

        query = query.limit(limit)

        result = await db.execute(query)
        items = result.scalars().all()

        return items

    except Exception as e:
        logger.error(f"❌ Failed to list memory items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_memory(search: SearchRequest):
    """Search memory using RAG (semantic search via Qdrant)"""
    try:
        memory_service = MemoryService()
        results = await memory_service.search(
            query=search.query,
            limit=search.limit,
            filter_type=search.type,
        )

        return {"results": results, "count": len(results)}

    except Exception as e:
        logger.error(f"❌ Failed to search memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{item_id}/approve")
async def approve_memory_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Approve a memory item and embed it in Qdrant"""
    try:
        result = await db.execute(select(MemoryItem).where(MemoryItem.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Memory item not found")

        if item.approved:
            return {"message": "Already approved", "item_id": item_id}

        # Approve and embed
        item.approved = True
        memory_service = MemoryService()
        vector_id = await memory_service.embed_memory_item(item)
        item.vector_id = vector_id

        await db.commit()

        logger.info(f"✅ Approved memory item #{item_id}")
        return {"message": "Memory item approved and embedded", "item_id": item_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to approve memory item: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
