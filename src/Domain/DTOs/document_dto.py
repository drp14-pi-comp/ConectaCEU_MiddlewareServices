"""DTOs for Document operations"""
from typing import Optional
from pydantic import BaseModel, Field

class DocumentCreateDTO(BaseModel):
    """DTO for uploading a document"""
    base64: str
    is_front: Optional[bool] = None
    user_id: str  # UUID as string
    document_type_id: int
    legal_representative_id: Optional[str] = None  # UUID as string

class DocumentValidationDTO(BaseModel):
    """DTO for validating a document"""
    document_id: str  # UUID as string
    document_validation_status_type_id: int
    rejection_reason: Optional[str] = Field(None, max_length=500)