"""DTOs for User operations"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from src.domain.dtos.address_dto import AddressCreateDTO
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.dtos.legal_representative_dto import LegalRepresentativeCreateDTO

class UserCreateDTO(BaseModel):
    """DTO for creating a new user"""
    # User
    document: str = Field(..., min_length=11, max_length=11)
    name: str = Field(..., min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    cellphone_number: Optional[str] = Field(None, pattern=r'^\d{9}$')
    contact_cellphone_number: Optional[str] = Field(None, pattern=r'^\d{9}$')
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    birthdate: date
    school: Optional[str] = Field(None, max_length=200)
    sex_id: int
    gender_id: int
    user_type_id: int
    
    # Uploaded documents
    id_document_front: DocumentCreateDTO
    id_document_back: DocumentCreateDTO
    user_photo: DocumentCreateDTO
    health_certificate: Optional[DocumentCreateDTO]

    # Address
    address: AddressCreateDTO

    # Legal representatives
    legal_representative_1: Optional[LegalRepresentativeCreateDTO]
    legal_representative_2: Optional[LegalRepresentativeCreateDTO]

    # Flag to indicate if this is a public registration
    is_public_registration: bool = False
    
    @field_validator('document')
    def validate_cpf(cls, v: str) -> str:
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        return cpf

class UserUpdateDTO(BaseModel):
    """DTO for updating user information"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    cellphone_number: Optional[str] = Field(None, pattern=r'^\d{9}$')
    contact_cellphone_number: Optional[str] = Field(None, pattern=r'^\d{9}$')
    school: Optional[str] = Field(None, max_length=200)
    sex_id: Optional[int] = None
    gender_id: Optional[int] = None
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}

class UserLoginDTO(BaseModel):
    """DTO for user login"""
    document: str
    password: str

class PasswordChangeDTO(BaseModel):
    """DTO for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    @field_validator('confirm_password')
    def passwords_match(cls, v: str, info) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

class PasswordResetRequestDTO(BaseModel):
    """DTO for password reset request"""
    email: EmailStr

class PasswordResetDTO(BaseModel):
    """DTO for password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    @field_validator('confirm_password')
    def passwords_match(cls, v: str, info) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserFilterDTO(BaseModel):
    """DTO for filtering users"""
    name: Optional[str] = None
    document: Optional[str] = None
    email: Optional[str] = None
    user_type_id: Optional[int] = None
    active: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)