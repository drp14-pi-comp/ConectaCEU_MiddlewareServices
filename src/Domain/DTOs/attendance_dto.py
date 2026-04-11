"""DTOs for Attendance operations"""
from typing import Optional
from pydantic import BaseModel

class AttendanceCreateDTO(BaseModel):
    """DTO for creating attendance records"""
    user_id: str  # UUID as string
    class_session_id: str  # UUID as string

class AttendanceUpdateDTO(BaseModel):
    """DTO for updating attendance"""
    attended: bool

class BulkAttendanceCreateDTO(BaseModel):
    """DTO for creating multiple attendance records"""
    class_session_id: str  # UUID as string
    user_ids: list[str]  # List of UUIDs as strings