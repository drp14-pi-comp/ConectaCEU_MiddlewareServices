"""Class session view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ClassSessionViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    date: datetime
    class_id: UUID
    
    model_config = ConfigDict(from_attributes=True)