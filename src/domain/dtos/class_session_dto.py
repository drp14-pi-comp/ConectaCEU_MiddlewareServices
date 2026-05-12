"""DTOs for Class Session operations"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ClassSessionCreateDTO(BaseModel):
    """DTO for creating a new class session"""
    date: datetime
    class_id: str  # UUID as string

class ClassSessionFilterDTO(BaseModel):
    """DTO for filtering class sessions"""
    class_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)