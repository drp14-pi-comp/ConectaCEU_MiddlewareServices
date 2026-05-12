"""Document domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class Document(BaseModel):
    """Document domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    base64: str
    is_front: Optional[bool] = None
    user_id: UUID
    document_type_id: int
    legal_representative_id: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)