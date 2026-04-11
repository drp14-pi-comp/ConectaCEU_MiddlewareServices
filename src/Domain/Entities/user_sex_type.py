"""User sex type domain entity"""
from pydantic import BaseModel, ConfigDict

class UserSexType(BaseModel):
    """User sex type reference entity"""
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)