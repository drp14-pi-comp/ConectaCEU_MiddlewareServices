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
    """DTO for submitting all attendances for a session at once"""
    class_session_id: str  # UUID as string
    attendances: list[AttendanceEntryDTO]  # Complete list of students

class AttendanceEntryDTO(BaseModel):
    """Single attendance entry"""
    user_id: str  # UUID as string
    attended: bool