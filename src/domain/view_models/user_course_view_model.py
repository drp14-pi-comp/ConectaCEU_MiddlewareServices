"""User course enrollment view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserCourseViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    active: bool
    user_id: UUID
    course_id: UUID
    
    model_config = ConfigDict(from_attributes=True)