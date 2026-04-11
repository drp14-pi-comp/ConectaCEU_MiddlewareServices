"""Document view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DocumentViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    base64: str
    is_front: Optional[bool]
    user_id: UUID
    document_type_id: int
    legal_representative_id: Optional[UUID]
    
    model_config = ConfigDict(from_attributes=True)