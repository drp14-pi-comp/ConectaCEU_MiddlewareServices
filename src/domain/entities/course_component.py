"""Course component domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CourseComponent(BaseModel):
    """Course component (module/subject) domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    active: bool = True
    course_id: UUID
    
    model_config = ConfigDict(from_attributes=True)