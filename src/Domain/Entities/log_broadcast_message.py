"""Broadcast message log domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogBroadcastMessage(BaseModel):
    """Broadcast message log domain entity"""
    
    id: UUID
    created_at: datetime
    message: str
    document_1_base64: str
    document_2_base64: str
    sent_whatsapp: bool = False
    sent_email: bool = False
    sent_sms: bool = False
    user_ip_address: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)