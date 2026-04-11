"""Legal representative domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

class LegalRepresentative(BaseModel):
    """Legal representative domain entity (for minors)"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    name: str = Field(..., min_length=3, max_length=200)
    document: str = Field(..., min_length=11, max_length=11)
    user_id: UUID
    
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