"""User domain entity"""
from datetime import datetime, date
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
import re

from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class User(BaseModel):
    """User domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    document: str = Field(..., min_length=11, max_length=11)
    name: str = Field(..., min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    cellphone_number: Optional[str] = Field(None, pattern=r'^\d{9}$')
    contact_cellphone_number: Optional[str] = Field(None, pattern=r'^\d{9}$')
    password: str
    birthdate: date
    school: Optional[str] = Field(None, max_length=200)
    active: bool = True
    sex_id: int
    gender_id: int
    user_type_id: int
    email_verified: Optional[bool] = None
    student_sequential: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('document')
    def validate_cpf(cls, v: str) -> str:
        """Validate CPF format"""
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        if cpf == cpf[0] * 11:
            raise ValueError('CPF inválido')
        return cpf
    
    @property
    def age(self) -> int:
        """Calculate user's age"""
        today = date.today()
        age = today.year - self.birthdate.year
        if today.month < self.birthdate.month or (
            today.month == self.birthdate.month and today.day < self.birthdate.day
        ):
            age -= 1
        return age
    
    @property
    def is_adult(self) -> bool:
        """Check if user is 18 or older"""
        return self.age >= 18
    
    @property
    def is_health_certificate_required(self) -> bool:
        """Check if user is 70 or older"""
        return self.age >= 70
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self.active = False
        self.updated_at = DateTimeHandler.now()
    
    def activate(self) -> None:
        """Activate user account"""
        self.active = True
        self.updated_at = DateTimeHandler.now()