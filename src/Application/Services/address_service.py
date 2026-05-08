"""Address service - business logic for Address entity"""
from typing import List, Optional
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.address_repository import AddressRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.address_dto import AddressCreateDTO, AddressUpdateDTO
from src.domain.view_models.address_view_model import AddressViewModel

class AddressService(BaseService):
    """Service for Address business logic"""
    
    def __init__(self, repository: AddressRepository):
        super().__init__(repository, 'address', mapper_class=ModelToEntityMapper)
        self.repository = repository
    
    async def create_address(self, dto: AddressCreateDTO) -> AddressViewModel:
        """Create a new address"""
        try:
            entity = DtoToEntityMapper.address(dto)
            model = EntityToModelMapper.address(entity)
            saved_model = await self.repository.create(model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.address(saved_model)
            return EntityToViewModelMapper.address(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def update_address(self, address_id: UUID, dto: AddressUpdateDTO) -> AddressViewModel:
        """Update an address"""
        try:
            model = await self.repository.get_by_id(address_id)
            if not model:
                raise ValueError("Address not found")
            
            entity = ModelToEntityMapper.address(model)
            updated_entity = UpdateMapper.address(entity, dto)
            updated_model = EntityToModelMapper.address(updated_entity)
            saved_model = await self.repository.update(updated_model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.address(saved_model)
            return EntityToViewModelMapper.address(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_user_addresses(self, user_id: UUID) -> List[AddressViewModel]:
        try:
            """Get all addresses for a user"""
            models = await self.repository.get_by_user_id(user_id)
            entities = [ModelToEntityMapper.address(model) for model in models]
            return [EntityToViewModelMapper.address(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_primary_address(self, user_id: UUID) -> Optional[AddressViewModel]:
        """Get user's primary address"""
        try:
            model = await self.repository.get_primary_address(user_id)
            if model:
                entity = ModelToEntityMapper.address(model)
                return EntityToViewModelMapper.address(entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)