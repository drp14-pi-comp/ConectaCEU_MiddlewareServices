"""User password history view model"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class UserPasswordHistoryViewModel(BaseModel):
    id: UUID
    created_at: datetime
    password: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)