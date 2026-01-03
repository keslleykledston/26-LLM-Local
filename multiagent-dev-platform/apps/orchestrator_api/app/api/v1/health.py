"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import httpx
from loguru import logger

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "services": {},
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if response.status_code == 200:
                health_status["services"]["ollama"] = "healthy"
            else:
                health_status["services"]["ollama"] = "unhealthy"
                health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        health_status["services"]["ollama"] = "unreachable"
        health_status["status"] = "degraded"

    # Check Qdrant
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.QDRANT_URL}/health", timeout=5.0)
            if response.status_code == 200:
                health_status["services"]["qdrant"] = "healthy"
            else:
                health_status["services"]["qdrant"] = "unhealthy"
                health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        health_status["services"]["qdrant"] = "unreachable"
        health_status["status"] = "degraded"

    return health_status


@router.get("/ollama/models")
async def list_ollama_models():
    """List available Ollama models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "models": [model["name"] for model in data.get("models", [])],
                    "count": len(data.get("models", [])),
                }
            else:
                return {"error": "Failed to fetch models", "status_code": response.status_code}
    except Exception as e:
        logger.error(f"Failed to list Ollama models: {e}")
        return {"error": str(e)}
