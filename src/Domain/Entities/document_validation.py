"""Document validation domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class DocumentValidation(BaseModel):
    """Document validation domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    rejection_reason: Optional[str] = Field(None, max_length=500)
    document_validation_status_type_id: int
    document_id: UUID
    
    model_config = ConfigDict(from_attributes=True)