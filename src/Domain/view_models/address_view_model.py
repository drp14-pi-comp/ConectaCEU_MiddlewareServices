"""Address view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AddressViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    zip_code: str
    street: str
    number: str
    complement: Optional[str]
    neighborhood: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)