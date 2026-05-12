"""StudentAbsenceJustification ViewModel"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class StudentAbsenceJustificationViewModel(BaseModel):
    id: UUID
    created_at: datetime
    class_attendance_id: UUID
    document_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)