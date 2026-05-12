"""Course domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class Course(BaseModel):
    """Course domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    name: str = Field(..., min_length=3, max_length=100)
    total_seat_limit: int = Field(..., ge=1)
    workload: int = Field(..., ge=1)
    active: bool = True
    responsible_educator_1: UUID
    responsible_educator_2: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    def deactivate(self) -> None:
        """Deactivate course"""
        self.active = False
        self.updated_at = DateTimeHandler.now()
    
    def activate(self) -> None:
        """Activate course"""
        self.active = True
        self.updated_at = DateTimeHandler.now()