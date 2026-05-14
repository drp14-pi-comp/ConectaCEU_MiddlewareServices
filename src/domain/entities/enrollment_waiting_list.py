from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EnrollmentWaitingList(BaseModel):
    """Enrollment waiting list entity"""
    
    id: UUID
    created_at: datetime
    user_id: UUID
    course_id: UUID
    position: int

    model_config = ConfigDict(from_attributes=True)
