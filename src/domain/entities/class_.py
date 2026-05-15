"""Class domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class Class(BaseModel):
    """Class domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    seats_in_use: int = Field(0, ge=0)
    active: bool = True
    date: datetime
    course_component_id: UUID
    
    model_config = ConfigDict(from_attributes=True)