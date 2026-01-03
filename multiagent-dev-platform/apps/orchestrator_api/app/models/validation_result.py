"""
Validation Result model - lint, test, build results
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ValidationResult(Base):
    """Validation result model"""

    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), index=True)
    validation_type = Column(String(50), nullable=False)  # lint, test, build
    success = Column(Boolean, nullable=False)
    output = Column(Text)
    errors = Column(JSON)
    warnings = Column(JSON)
    duration_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mission = relationship("Mission", back_populates="validation_results")

    def __repr__(self):
        return f"<ValidationResult(id={self.id}, type={self.validation_type}, success={self.success})>"
