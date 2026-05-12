"""DTOs for User Sex Type operations"""
from typing import Optional
from pydantic import BaseModel, Field

class UserSexTypeCreateDTO(BaseModel):
    """DTO for creating a user sex type"""
    description: str = Field(..., min_length=3, max_length=9)

class UserSexTypeUpdateDTO(BaseModel):
    """DTO for updating a user sex type"""
    description: Optional[str] = Field(None, min_length=3, max_length=9)
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}