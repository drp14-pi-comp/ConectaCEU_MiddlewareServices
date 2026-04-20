"""DTOs for Shift Type operations"""
from typing import Optional
from pydantic import BaseModel, Field

class ShiftTypeCreateDTO(BaseModel):
    """DTO for creating a shift type"""
    description: str = Field(..., min_length=3, max_length=50)

class ShiftTypeUpdateDTO(BaseModel):
    """DTO for updating a shift type"""
    description: Optional[str] = Field(None, min_length=3, max_length=50)
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}