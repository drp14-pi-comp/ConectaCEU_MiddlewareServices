"""Document validation status type domain entity"""
from pydantic import BaseModel, ConfigDict

class DocumentValidationStatusType(BaseModel):
    """Document validation status type reference entity"""
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)