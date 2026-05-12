"""DTOs for Class operations"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class ClassCreateDTO(BaseModel):
    """DTO for creating a new class"""
    component_id: str  # UUID as string
    shift_type_id: int

class ClassUpdateDTO(BaseModel):
    """DTO for updating a class"""
    active: Optional[bool] = None
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}

class ClassFilterDTO(BaseModel):
    """DTO for filtering classes"""
    component_id: Optional[str] = None
    shift_type_id: Optional[int] = None
    active: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

class ClassBulkCreateDTO(BaseModel):
    """DTO for creating classes and sessions in bulk"""
    # Course selection
    course_id: str  # UUID as string
    course_component_id: str  # UUID as string
    
    # Shift selections
    shift_type_ids: List[int] = Field(..., min_length=1)
    
    # Date range for sessions
    start_date: date
    end_date: date
    
    # Session schedule
    days_of_week: List[int] = Field(
        default=[0, 1, 2, 3, 4, 5, 6],  # 0=Monday, 6=Sunday
        description="Days of week for sessions (0=Monday, 6=Sunday)"
    )
    
    # Limits
    total_seat_limit_per_class: int = Field(..., ge=1)
    enrollment_seat_limit: int = Field(..., ge=1)
    
    @field_validator('end_date')
    def end_after_start(cls, v: str, info) -> str:
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('Data final deve ser porterior à data inicial')
        return v
    
    @field_validator('enrollment_seat_limit')
    def enrollment_not_exceed_total(cls, v: int, info) -> int:
        """Enrollment limit must not exceed total seat limit"""
        if 'total_seat_limit_per_class' in info.data and v > info.data['total_seat_limit_per_class']:
            raise ValueError('O limite de matrículas não pode ultrapassar o total de vagas')
        return v