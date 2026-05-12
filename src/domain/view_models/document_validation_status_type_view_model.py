"""Document validation status type view model"""
from pydantic import BaseModel, ConfigDict

class DocumentValidationStatusTypeViewModel(BaseModel):
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)