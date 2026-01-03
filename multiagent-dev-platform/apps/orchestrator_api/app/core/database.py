"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

from app.core.config import settings

# Convert postgres:// to postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database - create tables if they don't exist"""
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import (
                mission,
                task,
                agent_execution,
                device,
                external_ai_call,
                memory_item,
                validation_result,
            )

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.success("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
