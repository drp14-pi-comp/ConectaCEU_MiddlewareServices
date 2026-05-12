"""Address domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class Address(BaseModel):
    """Address domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    zip_code: str = Field(..., min_length=8, max_length=8)
    street: str = Field(..., min_length=3, max_length=200)
    number: str = Field(..., max_length=10)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: str = Field(..., min_length=3, max_length=100)
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
    
    def full_address(self) -> str:
        """Return formatted full address"""
        address = f"{self.street}, {self.number}"
        if self.complement:
            address += f" - {self.complement}"
        address += f", {self.neighborhood} - CEP: {self.zip_code}"
        return address