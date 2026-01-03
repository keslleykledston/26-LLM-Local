"""
Mission model - represents a development mission
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Mission(Base):
    """Mission model"""

    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="planning", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(100))
    plan = Column(JSON)
    mission_metadata = Column(JSON)

    # Relationships
    tasks = relationship("Task", back_populates="mission", cascade="all, delete-orphan")
    external_ai_calls = relationship(
        "ExternalAICall", back_populates="mission", cascade="all, delete-orphan"
    )
    validation_results = relationship(
        "ValidationResult", back_populates="mission", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Mission(id={self.id}, title={self.title}, status={self.status})>"
