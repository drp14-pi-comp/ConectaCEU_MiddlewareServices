"""Course component view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class CourseComponentViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    name: str
    description: str
    seat_limit_per_class: int
    active: bool
    course_id: UUID
    
    model_config = ConfigDict(from_attributes=True)