"""Course view model"""
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.domain.view_models.course_component_view_model import CourseComponentViewModel

class CourseViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    name: str
    total_seat_limit: int
    workload: int
    active: bool
    responsible_educator_1: UUID
    responsible_educator_2: Optional[UUID] = None

    course_components: Optional[List[CourseComponentViewModel]] = None
    
    model_config = ConfigDict(from_attributes=True)