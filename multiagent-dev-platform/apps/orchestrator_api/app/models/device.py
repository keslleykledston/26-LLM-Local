"""
Device model - network inventory entry for SSH access
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Device(Base):
    """Network device inventory"""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    vendor = Column(String(50), nullable=False)
    platform = Column(String(50), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False, default=22)
    username = Column(String(100), nullable=False)
    password_encrypted = Column(Text)
    enable_password_encrypted = Column(Text)
    last_error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Device(id={self.id}, name={self.name}, platform={self.platform}, host={self.host})>"
