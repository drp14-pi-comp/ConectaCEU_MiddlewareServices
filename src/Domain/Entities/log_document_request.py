"""Document request log domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogDocumentRequest(BaseModel):
    """Document request log domain entity"""
    
    id: UUID
    created_at: datetime
    user_ip_address: str
    document_type_id: int
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)