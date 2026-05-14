"""DTOs for User Course enrollment operations"""
from pydantic import BaseModel

class UserCourseEnrollDTO(BaseModel):
    """DTO for enrolling a user in a class"""
    user_id: str  # UUID as string
    course_id: str  # UUID as string

class UserCourseBulkEnrollDTO(BaseModel):
    """DTO for enrolling multiple users in a class"""
    course_id: str  # UUID as string
    user_ids: list[str]  # List of UUIDs as strings