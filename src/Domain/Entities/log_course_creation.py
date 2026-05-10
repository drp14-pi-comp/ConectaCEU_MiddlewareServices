"""Course creation log domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogCourseCreation(BaseModel):
    """Course creation log domain entity"""
    
    id: UUID
    created_at: datetime
    name: str
    total_seat_limit: int
    workload: int
    active: bool
    user_ip_address: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)