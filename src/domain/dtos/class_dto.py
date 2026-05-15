"""DTOs for Class operations"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class ClassCreateDTO(BaseModel):
    """DTO for creating a new class"""
    component_id: str  # UUID as string
    date: datetime

class ClassUpdateDTO(BaseModel):
    """DTO for updating a class"""
    active: Optional[bool] = None
    date: Optional[datetime] = None

class ClassFilterDTO(BaseModel):
    """DTO for filtering classes"""
    component_id: Optional[str] = None
    active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

class ClassBulkCreateDTO(BaseModel):
    course_component_id: str
    start_date: date
    end_date: date
    days_of_week: List[int] = Field(default=[0, 1, 2, 3, 4, 5, 6])
    seats_to_use: int = Field(5, ge=5)
    
    @field_validator('end_date')
    def end_after_start(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('Data final deve ser posterior à data inicial')
        return v
    
    @field_validator('days_of_week')
    def days_received_in_range(cls, v):
        valid_days = {0, 1, 2, 3, 4, 5, 6}
        for day in v:
            if day not in valid_days:
                raise ValueError(f'{day} não é um dia da semana válido (0-6)')
        return v