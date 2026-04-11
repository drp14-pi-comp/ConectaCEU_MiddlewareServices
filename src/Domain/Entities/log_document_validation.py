"""Document validation log domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class LogDocumentValidation(BaseModel):
    """Document validation log domain entity"""
    
    id: UUID
    created_at: datetime
    rejection_reason: Optional[str] = None
    activated: bool
    performed_user_ip_address: str
    user_id: UUID
    performed_by_user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)