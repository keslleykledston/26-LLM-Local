"""
Task model - represents individual tasks within missions
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    """Task model"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), index=True)
    agent_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    result = Column(JSON)
    error = Column(Text)
    task_metadata = Column(JSON)

    # Relationships
    mission = relationship("Mission", back_populates="tasks")
    agent_executions = relationship(
        "AgentExecution", back_populates="task", cascade="all, delete-orphan"
    )
    external_ai_calls = relationship(
        "ExternalAICall", back_populates="task", foreign_keys="ExternalAICall.task_id"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, agent={self.agent_type}, status={self.status})>"
