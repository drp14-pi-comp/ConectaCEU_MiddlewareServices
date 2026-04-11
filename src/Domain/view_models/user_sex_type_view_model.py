"""User sex type view model"""
from pydantic import BaseModel, ConfigDict

class UserSexTypeViewModel(BaseModel):
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)