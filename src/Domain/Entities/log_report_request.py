"""Report request log domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogReportRequest(BaseModel):
    """Report request log domain entity"""
    
    id: UUID
    created_at: datetime
    report_type_id: int
    user_ip_address: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)