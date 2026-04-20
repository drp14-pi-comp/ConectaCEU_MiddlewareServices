"""Document validation service - business logic for Document Validation entity"""
from typing import List
from uuid import UUID

from src.data.repositories.document_validation_repository import DocumentValidationRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.document_validation_dto import DocumentValidationCreateDTO, DocumentValidationUpdateDTO
from src.domain.view_models.document_validation_view_model import DocumentValidationViewModel

class DocumentValidationService(BaseService):
    """Service for Document Validation business logic"""
    
    def __init__(self, repository: DocumentValidationRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create_validation(self, dto: DocumentValidationCreateDTO) -> DocumentValidationViewModel:
        """Create a document validation (pending status)"""
        existing = await self.repository.get_by_document_id(UUID(dto.document_id))
        if existing:
            raise ValueError("Validation already exists for this document")
        
        entity = DtoToEntityMapper.document_validation(dto)
        model = EntityToModelMapper.document_validation(entity)
        saved_model = await self.repository.create(model)
        saved_entity = ModelToEntityMapper.document_validation(saved_model)
        return EntityToViewModelMapper.document_validation(saved_entity)
    
    async def update_validation(self, validation_id: UUID, dto: DocumentValidationUpdateDTO) -> DocumentValidationViewModel:
        """Update a document validation (approve/reject)"""
        model = await self.repository.get_by_id(validation_id)
        if not model:
            raise ValueError("Validation not found")
        
        entity = ModelToEntityMapper.document_validation(model)
        updated_entity = UpdateMapper.document_validation(entity, dto)
        updated_model = EntityToModelMapper.document_validation(updated_entity)
        saved_model = await self.repository.update(updated_model)
        saved_entity = ModelToEntityMapper.document_validation(saved_model)
        return EntityToViewModelMapper.document_validation(saved_entity)
    
    async def approve_document(self, validation_id: UUID) -> DocumentValidationViewModel:
        """Approve a document"""
        dto = DocumentValidationUpdateDTO(
            document_validation_status_type_id=2,  # Approved
            rejection_reason=None
        )
        return await self.update_validation(validation_id, dto)
    
    async def reject_document(self, validation_id: UUID, reason: str) -> DocumentValidationViewModel:
        """Reject a document with reason"""
        dto = DocumentValidationUpdateDTO(
            document_validation_status_type_id=3,  # Rejected
            rejection_reason=reason
        )
        return await self.update_validation(validation_id, dto)
    
    async def get_pending_validations(self, skip: int = 0, limit: int = 100) -> List[DocumentValidationViewModel]:
        """Get pending document validations"""
        models = await self.repository.get_pending_validations(skip, limit)
        entities = [ModelToEntityMapper.document_validation(model) for model in models]
        return [EntityToViewModelMapper.document_validation(entity) for entity in entities]
    
    async def get_validation_by_document(self, document_id: UUID) -> DocumentValidationViewModel:
        """Get validation for a document"""
        model = await self.repository.get_by_document_id(document_id)
        if not model:
            raise ValueError("Validation not found for this document")
        
        entity = ModelToEntityMapper.document_validation(model)
        return EntityToViewModelMapper.document_validation(entity)