"""
Memory Item model - approved content for RAG
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ARRAY
from sqlalchemy.sql import func

from app.core.database import Base


class MemoryItem(Base):
    """Memory item for RAG"""

    __tablename__ = "memory_items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)  # adr, playbook, snippet, glossary
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    tags = Column(ARRAY(String))
    vector_id = Column(String(100))  # Reference to Qdrant vector
    approved = Column(Boolean, default=False, index=True)
    approved_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    item_metadata = Column(JSON)

    def __repr__(self):
        return f"<MemoryItem(id={self.id}, type={self.type}, title={self.title}, approved={self.approved})>"
