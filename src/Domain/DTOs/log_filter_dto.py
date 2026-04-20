"""DTOs for filtering logs"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class LogFilterDTO(BaseModel):
    """Base DTO for filtering logs"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

class LogUserActivationFilterDTO(LogFilterDTO):
    """DTO for filtering user activation logs"""
    user_id: Optional[str] = None
    performed_by_user_id: Optional[str] = None
    activated: Optional[bool] = None

class LogBroadcastMessageFilterDTO(LogFilterDTO):
    """DTO for filtering broadcast message logs"""
    user_id: Optional[str] = None
    sent_whatsapp: Optional[bool] = None
    sent_email: Optional[bool] = None
    sent_sms: Optional[bool] = None

class LogCourseCreationFilterDTO(LogFilterDTO):
    """DTO for filtering course creation logs"""
    user_id: Optional[str] = None
    course_id: Optional[str] = None

class LogDocumentRequestFilterDTO(LogFilterDTO):
    """DTO for filtering document request logs"""
    user_id: Optional[str] = None
    document_type_id: Optional[int] = None

class LogDocumentValidationFilterDTO(LogFilterDTO):
    """DTO for filtering document validation logs"""
    user_id: Optional[str] = None
    performed_by_user_id: Optional[str] = None
    activated: Optional[bool] = None

class LogReportRequestFilterDTO(LogFilterDTO):
    """DTO for filtering report request logs"""
    user_id: Optional[str] = None
    report_type_id: Optional[int] = None

class LogStudentEnrollmentFilterDTO(LogFilterDTO):
    """DTO for filtering student enrollment logs"""
    user_id: Optional[str] = None
    course_id: Optional[str] = None
    enrolled: Optional[bool] = None

class LogApplicationErrorFilterDTO(LogFilterDTO):
    """DTO for filtering application error logs"""
    # No additional filters needed
    pass