"""Class domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class Class(BaseModel):
    """Class domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    seats_in_use: int = Field(0, ge=0)
    active: bool = True
    component_id: UUID
    shift_type_id: int
    
    model_config = ConfigDict(from_attributes=True)
    
    def has_available_seats(self, seat_limit: int) -> bool:
        """Check if class has available seats"""
        return self.seats_in_use < seat_limit