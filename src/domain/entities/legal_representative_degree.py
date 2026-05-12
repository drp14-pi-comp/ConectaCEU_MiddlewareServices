"""Legal representative degree entity"""
from pydantic import BaseModel, ConfigDict

class LegalRepresentativeDegree(BaseModel):
    """Document type reference entity"""
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)