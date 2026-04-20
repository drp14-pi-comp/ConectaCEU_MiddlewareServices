"""DTOs for Document Validation operations"""
from typing import Optional
from pydantic import BaseModel, Field

class DocumentValidationCreateDTO(BaseModel):
    """DTO for creating a document validation"""
    document_id: str  # UUID as string
    document_validation_status_type_id: int = Field(1, ge=1, le=3)

class DocumentValidationUpdateDTO(BaseModel):
    """DTO for updating a document validation"""
    document_validation_status_type_id: int = Field(..., ge=1, le=3)
    rejection_reason: Optional[str] = Field(None, max_length=500)
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}

class BulkDocumentValidationDTO(BaseModel):
    """DTO for bulk validating documents"""
    validations: list[DocumentValidationUpdateDTO]