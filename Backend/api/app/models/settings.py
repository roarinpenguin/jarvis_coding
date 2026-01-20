"""Database models for application settings"""
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime

from app.models.destination import Base


class Setting(Base):
    """Key-value settings storage"""
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
