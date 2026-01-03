"""
External AI Call model - audit trail of external AI usage
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExternalAICall(Base):
    """External AI call audit log"""

    __tablename__ = "external_ai_calls"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    provider = Column(String(100), nullable=False)
    model = Column(String(100))
    purpose = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)
    approved = Column(Boolean, default=False, index=True)
    approved_by = Column(String(100))
    approved_at = Column(DateTime(timezone=True))
    request = Column(JSON)
    response = Column(JSON)
    tokens_used = Column(Integer)
    cost_usd = Column(Numeric(10, 6))
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mission = relationship("Mission", back_populates="external_ai_calls")
    task = relationship("Task", back_populates="external_ai_calls", foreign_keys=[task_id])

    def __repr__(self):
        return f"<ExternalAICall(id={self.id}, provider={self.provider}, approved={self.approved}, cached={self.cached})>"
