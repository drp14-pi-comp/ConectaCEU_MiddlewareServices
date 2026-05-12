"""User password history domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class UserPasswordHistory(BaseModel):
    """User password history domain entity"""
    
    id: UUID
    created_at: datetime
    password: str
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)