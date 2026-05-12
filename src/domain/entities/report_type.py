"""Report type domain entity"""
from pydantic import BaseModel, ConfigDict

class ReportType(BaseModel):
    """Report type reference entity"""
    id: int
    description: str
    
    model_config = ConfigDict(from_attributes=True)