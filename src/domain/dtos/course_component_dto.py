"""DTOs for Course Component operations"""
from typing import Optional
from pydantic import BaseModel, Field

class CourseComponentCreateDTO(BaseModel):
    """DTO for creating a new course component"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    course_id: Optional[str] = Field(None)  # UUID as string

class CourseComponentUpdateDTO(BaseModel):
    """DTO for updating a course component"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    active: Optional[bool] = None
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}