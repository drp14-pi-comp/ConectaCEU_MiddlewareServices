"""DTOs for Legal Representative operations"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re

from src.domain.dtos.document_dto import DocumentCreateDTO

class LegalRepresentativeCreateDTO(BaseModel):
    """DTO for creating a legal representative"""
    name: str = Field(..., min_length=3, max_length=200)
    document: str = Field(..., min_length=11, max_length=11)
    user_id: Optional[str] = None  # UUID as string
    legal_representative_degree_id: int

    # Documents
    id_document_front: DocumentCreateDTO
    id_document_back: DocumentCreateDTO
    student_registry_authorization: DocumentCreateDTO
    
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
    legal_representative_degree_id: Optional[int] = Field(None)
    
    @field_validator('document')
    def validate_cpf(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        return cpf