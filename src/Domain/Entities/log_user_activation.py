"""User activation log domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class LogUserActivation(BaseModel):
    """User activation log domain entity"""
    
    id: UUID
    created_at: datetime
    deactivation_reason: Optional[str] = None
    activated: bool
    performed_by_user_ip_address: str
    user_id: UUID
    performed_by_user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)