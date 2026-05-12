"""StudentAbsenceJustification domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class StudentAbsenceJustification(BaseModel):
    """Links an attendance record to a justification document."""
    id: UUID
    created_at: datetime
    class_attendance_id: UUID
    document_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)