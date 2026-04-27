"""DTOs for Document Validation operations"""
from typing import Optional
from pydantic import BaseModel, Field

class DocumentValidationDTO(BaseModel):
    """DTO for creating a document validation"""
    document_validation_status_type_id: int = Field(1, ge=1, le=3)
    document_id: Optional[str]  # UUID as string
    rejection_reason: Optional[str] = Field(None, max_length=500)