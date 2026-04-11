"""Class session domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ClassSession(BaseModel):
    """Class session domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    date: datetime
    class_id: UUID
    
    model_config = ConfigDict(from_attributes=True)