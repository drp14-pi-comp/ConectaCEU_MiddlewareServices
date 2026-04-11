"""DTOs for Attendance operations"""
from pydantic import BaseModel

class ClassAttendanceCreateDTO(BaseModel):
    """DTO for creating attendance records"""
    user_id: str  # UUID as string
    class_session_id: str  # UUID as string

class ClassAttendanceUpdateDTO(BaseModel):
    """DTO for updating attendance"""
    attended: bool

class BulkClassAttendanceCreateDTO(BaseModel):
    """DTO for creating multiple attendance records"""
    class_session_id: str  # UUID as string
    user_ids: list[str]  # List of UUIDs as strings