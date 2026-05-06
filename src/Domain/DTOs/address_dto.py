"""DTOs for Address operations"""
from typing import Optional
from pydantic import BaseModel, Field

class AddressCreateDTO(BaseModel):
    """DTO for creating a new address"""
    zip_code: str = Field(..., min_length=8, max_length=8)
    street: str = Field(..., min_length=3, max_length=200)
    number: str = Field(..., max_length=10)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: str = Field(..., min_length=3, max_length=100)
    user_id: Optional[str] = None  # UUID as string

class AddressUpdateDTO(BaseModel):
    """DTO for updating an address"""
    zip_code: Optional[str] = Field(None, min_length=8, max_length=8)
    street: Optional[str] = Field(None, min_length=3, max_length=200)
    number: Optional[str] = Field(None, max_length=10)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, min_length=3, max_length=100)