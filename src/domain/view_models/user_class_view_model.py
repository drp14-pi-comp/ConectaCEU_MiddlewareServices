"""User class enrollment view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserClassViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    active: bool
    user_id: UUID
    class_id: UUID
    
    model_config = ConfigDict(from_attributes=True)