"""Student enrollment log domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogStudentEnrollment(BaseModel):
    """Student enrollment log domain entity"""
    
    id: UUID
    created_at: datetime
    enrolled: bool
    user_ip_address: str
    user_id: UUID
    course_id: UUID
    
    model_config = ConfigDict(from_attributes=True)