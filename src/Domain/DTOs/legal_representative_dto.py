"""DTOs for Legal Representative operations"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re

class LegalRepresentativeCreateDTO(BaseModel):
    """DTO for creating a legal representative"""
    name: str = Field(..., min_length=3, max_length=200)
    document: str = Field(..., min_length=11, max_length=11)
    user_id: str  # UUID as string
    legal_representative_degree_id: int
    
    @field_validator('document')
    def validate_cpf(cls, v: str) -> str:
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        return cpf

class LegalRepresentativeUpdateDTO(BaseModel):
    """DTO for updating a legal representative"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    document: Optional[str] = Field(None, min_length=11, max_length=11)
    legal_representative_degree_id: int
    
    @field_validator('document')
    def validate_cpf(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        return cpf
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}