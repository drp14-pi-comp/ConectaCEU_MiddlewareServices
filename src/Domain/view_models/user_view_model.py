"""User view model"""
from datetime import datetime, date
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.domain.view_models.address_view_model import AddressViewModel
from src.domain.view_models.document_view_model import DocumentViewModel
from src.domain.view_models.legal_representative_view_model import LegalRepresentativeViewModel

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

class StudentUserViewModel(BaseModel):
    # User
    document: str
    name: str
    email: Optional[str]
    cellphone_number: Optional[str]
    contact_cellphone_number: Optional[str]
    password: str
    birthdate: date
    school: Optional[str]
    sex_id: int
    gender_id: int
    user_type_id: int
    
    # Uploaded documents
    id_document_front: DocumentViewModel
    id_document_back: DocumentViewModel
    user_photo: DocumentViewModel
    health_certificate: Optional[DocumentViewModel]

    # Address
    address: AddressViewModel

    # Legal representatives
    legal_representative_1: Optional[LegalRepresentativeViewModel]
    legal_representative_2: Optional[LegalRepresentativeViewModel]

    model_config = ConfigDict(from_attributes=True)