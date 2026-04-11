"""DTOs for Report operations"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ReportRequestDTO(BaseModel):
    """DTO for requesting a report"""
    report_type_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    course_id: Optional[str] = None  # UUID as string
    user_id: Optional[str] = None  # UUID as string