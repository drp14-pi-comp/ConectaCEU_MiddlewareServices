"""DTOs for User Gender Type operations"""
from typing import Optional
from pydantic import BaseModel, Field

class UserGenderTypeCreateDTO(BaseModel):
    """DTO for creating a user gender type"""
    description: str = Field(..., min_length=3, max_length=20)

class UserGenderTypeUpdateDTO(BaseModel):
    """DTO for updating a user gender type"""
    description: Optional[str] = Field(None, min_length=3, max_length=20)
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}