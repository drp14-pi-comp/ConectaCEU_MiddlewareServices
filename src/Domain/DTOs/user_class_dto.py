"""DTOs for User Class enrollment operations"""
from pydantic import BaseModel

class UserClassEnrollDTO(BaseModel):
    """DTO for enrolling a user in a class"""
    user_id: str  # UUID as string
    class_id: str  # UUID as string

class UserClassBulkEnrollDTO(BaseModel):
    """DTO for enrolling multiple users in a class"""
    class_id: str  # UUID as string
    user_ids: list[str]  # List of UUIDs as strings