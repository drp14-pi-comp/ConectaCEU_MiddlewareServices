"""Attendance domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class ClassAttendance(BaseModel):
    """Attendance domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    attended: bool = False
    user_id: UUID
    class_session_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
    
    def mark_attended(self) -> None:
        """Mark user as attended"""
        self.attended = True
        self.updated_at = DateTimeHandler.now()
    
    def mark_absent(self) -> None:
        """Mark user as absent"""
        self.attended = False
        self.updated_at = DateTimeHandler.now()