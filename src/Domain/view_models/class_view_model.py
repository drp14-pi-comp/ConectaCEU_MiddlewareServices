"""Class view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ClassViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    seats_in_use: int
    active: bool
    component_id: UUID
    shift_type_id: int
    
    model_config = ConfigDict(from_attributes=True)