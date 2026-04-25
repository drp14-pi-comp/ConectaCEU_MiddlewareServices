"""DTOs for Course operations"""
from typing import Optional
from pydantic import BaseModel, Field

from src.domain.dtos.course_component_dto import CourseComponentCreateDTO

class CourseCreateDTO(BaseModel):
    """DTO for creating a new course"""
    name: str = Field(..., min_length=3, max_length=100)
    total_seat_limit: int = Field(..., ge=1)
    workload: int = Field(..., ge=1)
    responsible_educator_1: str  # UUID as string
    responsible_educator_2: Optional[str] = None  # UUID as string
    components: list[CourseComponentCreateDTO]

class CourseUpdateDTO(BaseModel):
    """DTO for updating a course"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    total_seat_limit: Optional[int] = Field(None, ge=1)
    workload: Optional[int] = Field(None, ge=1)
    responsible_educator_1: Optional[str] = None
    responsible_educator_2: Optional[str] = None
    active: Optional[bool] = None
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}

class CourseFilterDTO(BaseModel):
    """DTO for filtering courses"""
    name: Optional[str] = None
    active: Optional[bool] = None
    responsible_educator_1: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)