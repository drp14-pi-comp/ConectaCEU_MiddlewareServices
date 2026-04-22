"""Legal representative service - business logic for Legal Representative entity"""
from typing import List
from uuid import UUID

from src.data.repositories.legal_representative_repository import LegalRepresentativeRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.legal_representative_dto import LegalRepresentativeCreateDTO, LegalRepresentativeUpdateDTO
from src.domain.view_models.legal_representative_view_model import LegalRepresentativeViewModel

class LegalRepresentativeService(BaseService):
    """Service for Legal Representative business logic"""
    
    def __init__(self, repository: LegalRepresentativeRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create_representative(self, dto: LegalRepresentativeCreateDTO) -> LegalRepresentativeViewModel:
        """Create a new legal representative"""
        # Check if document already exists
        if await self.repository.document_exists(dto.document):
            raise ValueError("Document already registered")
        
        entity = DtoToEntityMapper.legal_representative(dto)
        model = EntityToModelMapper.legal_representative(entity)
        saved_model = await self.repository.create(model)
        saved_entity = ModelToEntityMapper.legal_representative(saved_model)
        return EntityToViewModelMapper.legal_representative(saved_entity)
    
    async def update_representative(
        self,
        representative_id: UUID,
        dto: LegalRepresentativeUpdateDTO
    ) -> LegalRepresentativeViewModel:
        """Update a legal representative"""
        model = await self.repository.get_by_id(representative_id)
        if not model:
            raise ValueError("Representative not found")
        
        # Check document uniqueness if being updated
        if dto.document:
            exists = await self.repository.document_exists(dto.document, exclude_id=representative_id)
            if exists:
                raise ValueError("Document already registered")
        
        entity = ModelToEntityMapper.legal_representative(model)
        updated_entity = UpdateMapper.legal_representative(entity, dto)
        updated_model = EntityToModelMapper.legal_representative(updated_entity)
        saved_model = await self.repository.update(updated_model)
        saved_entity = ModelToEntityMapper.legal_representative(saved_model)
        return EntityToViewModelMapper.legal_representative(saved_entity)
    
    async def get_user_representatives(self, user_id: UUID) -> List[LegalRepresentativeViewModel]:
        """Get all legal representatives for a user"""
        models = await self.repository.get_by_user_id(user_id)
        entities = [ModelToEntityMapper.legal_representative(model) for model in models]
        return [EntityToViewModelMapper.legal_representative(entity) for entity in entities]