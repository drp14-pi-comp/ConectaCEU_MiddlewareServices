"""Document type view model"""
from pydantic import BaseModel, ConfigDict

class DocumentTypeViewModel(BaseModel):
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)