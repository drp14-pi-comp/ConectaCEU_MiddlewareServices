"""Generic reference service for all reference entities"""
from typing import List, Optional, Type, Any
from uuid import UUID

from src.data.repositories.base.base_repository import BaseRepository
from src.application.services.base_service import BaseService

class ReferenceService(BaseService):
    """Generic service for reference/lookup entities"""
    
    def __init__(self, repository: BaseRepository, entity_name: str):
        super().__init__(repository)
        self.repository = repository
        self.entity_name = entity_name
    
    async def get_all_active(self) -> List[Any]:
        """Get all active reference items"""
        models = await self.repository.get_all()
        entities = []
        for model in models:
            # Use dynamic import or registry pattern
            from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
            mapper_method = getattr(ModelToEntityMapper, self.entity_name.lower().replace('_', ''), None)
            if mapper_method:
                entities.append(mapper_method(model))
        return entities
    
    async def get_by_description(self, description: str) -> Optional[Any]:
        """Get reference item by description"""
        model = await self.repository.get_by_description(description)
        if model:
            from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
            mapper_method = getattr(ModelToEntityMapper, self.entity_name.lower().replace('_', ''), None)
            if mapper_method:
                return mapper_method(model)
        return None