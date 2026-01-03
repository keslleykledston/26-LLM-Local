"""
Multiagent Dev Platform - Main API Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
from pathlib import Path

from app.core.config import settings
from app.api.v1 import missions, agents, memory, external_ai, health

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    "logs/orchestrator.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
)

# Create FastAPI app
app = FastAPI(
    title="Multiagent Dev Platform",
    description="""
    🤖 A local-first, multiagent development platform powered by Ollama

    ## Features
    - 🏠 **Local-first**: Runs entirely on your machine using Ollama
    - 🧠 **Long-term Memory**: RAG-powered context using Qdrant
    - 👥 **Specialized Agents**: Frontend, Backend, QA, Database experts
    - 🔒 **Controlled External AI**: Only when justified and approved
    - ✅ **Quality Assurance**: Automatic linting, testing, building
    - 📚 **Knowledge Base**: ADRs, playbooks, snippets

    ## Pipeline
    PLAN → EXECUTE → VALIDATE → INTEGRATE → MEMORY
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
        },
    )

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(missions.router, prefix="/api/v1/missions", tags=["Missions"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(external_ai.router, prefix="/api/v1/external-ai", tags=["External AI"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Multiagent Dev Platform...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🧠 Ollama URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"🗄️ Qdrant URL: {settings.QDRANT_URL}")
    logger.info(f"🔒 Offline-only mode: {settings.OFFLINE_ONLY_MODE}")

    # Initialize database
    from app.core.database import init_db
    await init_db()

    # Initialize Qdrant collections
    from app.services.memory_service import MemoryService
    memory_service = MemoryService()
    await memory_service.initialize_collections()

    logger.success("✅ Platform ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down Multiagent Dev Platform...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Multiagent Dev Platform",
        "version": "1.0.0",
        "status": "running",
        "mode": "offline-first" if settings.OFFLINE_ONLY_MODE else "hybrid",
        "docs": "/docs",
    }
