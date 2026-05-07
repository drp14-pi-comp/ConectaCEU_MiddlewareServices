"""Base service with common business operations"""
from typing import Optional, List, Any
from uuid import UUID

from src.data.repositories.base.base_repository import BaseRepository
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper

class BaseService:
    """Generic service with common CRUD operations"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    async def get_by_id(self, id: UUID) -> Optional[Any]:
        """Get entity by ID"""
        model = await self.repository.get_by_id(id)
        if model:
            return ModelToEntityMapper.from_model(model)
        return None
    
    async def get_by_id_int(self, id: int) -> Optional[Any]:
        """Get entity by integer ID"""
        model = await self.repository.get_by_id_int(id)
        if model:
            return ModelToEntityMapper.from_model(model)
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all entities with pagination"""
        models = await self.repository.get_all(skip, limit)
        return [ModelToEntityMapper.from_model(model) for model in models]
    
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        result = await self.repository.delete(id)
        self.repository.session.commit()
        return True if result else False
    
    async def delete_int(self, id: int) -> bool:
        """Delete entity by integer ID"""
        result = await self.repository.delete_int(id)
        self.repository.session.commit()
        return True if result else False
    
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        return await self.repository.exists(id)
    
    async def exists_int(self, id: int) -> bool:
        """Check if entity with integer ID exists"""
        return await self.repository.exists_int(id)