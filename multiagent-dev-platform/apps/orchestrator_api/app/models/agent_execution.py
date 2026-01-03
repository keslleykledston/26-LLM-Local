"""
Agent Execution model - detailed log of agent actions
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AgentExecution(Base):
    """Agent execution log model"""

    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    agent_type = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    input = Column(JSON)
    output = Column(JSON)
    success = Column(Boolean, default=True)
    error = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="agent_executions")

    def __repr__(self):
        return f"<AgentExecution(id={self.id}, agent={self.agent_type}, action={self.action}, success={self.success})>"
