"""Application error log domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogApplicationError(BaseModel):
    """Application error log domain entity"""
    
    id: UUID
    created_at: datetime
    exception: str
    stacktrace: str
    
    model_config = ConfigDict(from_attributes=True)