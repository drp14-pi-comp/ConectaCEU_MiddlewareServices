"""User view model"""
from datetime import datetime, date
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserViewModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    document: str
    name: str
    email: Optional[str]
    cellphone_number: Optional[str]
    contact_cellphone_number: Optional[str]
    password: str
    birthdate: date
    school: Optional[str]
    active: bool
    sex_id: int
    gender_id: int
    user_type_id: int
    
    model_config = ConfigDict(from_attributes=True)