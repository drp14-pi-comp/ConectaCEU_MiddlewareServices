"""Document validation view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DocumentValidationViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    rejection_reason: Optional[str]
    document_validation_status_type_id: int
    document_id: UUID
    
    model_config = ConfigDict(from_attributes=True)