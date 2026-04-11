"""User gender type domain entity"""
from pydantic import BaseModel, ConfigDict

class UserGenderType(BaseModel):
    """User gender type reference entity"""
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)