"""DTOs for Class operations"""
from typing import Optional
from pydantic import BaseModel, Field

class ClassCreateDTO(BaseModel):
    """DTO for creating a new class"""
    component_id: str  # UUID as string
    shift_type_id: int

class ClassUpdateDTO(BaseModel):
    """DTO for updating a class"""
    active: Optional[bool] = None
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}

class ClassFilterDTO(BaseModel):
    """DTO for filtering classes"""
    component_id: Optional[str] = None
    shift_type_id: Optional[int] = None
    active: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)