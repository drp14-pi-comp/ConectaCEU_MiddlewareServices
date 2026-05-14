"""User course enrollment domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserCourse(BaseModel):
    """User course enrollment domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    active: bool = True
    user_id: UUID
    course_id: UUID
    
    model_config = ConfigDict(from_attributes=True)