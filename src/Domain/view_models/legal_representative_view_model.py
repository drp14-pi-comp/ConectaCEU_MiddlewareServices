"""Legal representative view model"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class LegalRepresentativeViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    name: str
    document: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)