"""Generic reference service for all reference entities"""
from typing import List, Any

from src.data.repositories.base.base_repository import BaseRepository
from src.application.services.base_service import BaseService

class ReferenceService(BaseService):
    """Generic service for reference/lookup entities"""
    
    def __init__(self, repository: BaseRepository, entity_name: str):
        super().__init__(repository)
        self.repository = repository
        self.entity_name = entity_name
    
    async def get_all_active(self) -> List[Any]:
        models = await self.repository.get_all()
        from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
        
        mapper_method = self._get_mapper_method(ModelToEntityMapper)
        if mapper_method:
            return [mapper_method(model) for model in models]
        return []
    
    def _get_mapper_method(self, mapper):
        """Get the mapper method by converting entity name to snake_case"""
        method_name = self._camel_to_snake(self.entity_name)
        return getattr(mapper, method_name, None)
    
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert CamelCase to snake_case"""
        import re
        # Insert underscore between lowercase and uppercase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        # Insert underscore between lowercase/number and uppercase
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()