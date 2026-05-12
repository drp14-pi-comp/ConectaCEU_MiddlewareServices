"""DTOs for Document Validation Status Type operations"""
from typing import Optional
from pydantic import BaseModel, Field

class DocumentValidationStatusTypeCreateDTO(BaseModel):
    """DTO for creating a validation status type"""
    description: str = Field(..., min_length=3, max_length=50)

class DocumentValidationStatusTypeUpdateDTO(BaseModel):
    """DTO for updating a validation status type"""
    description: Optional[str] = Field(None, min_length=3, max_length=50)
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}