"""Class service - business logic for Class entity"""
from typing import List, Optional
from uuid import UUID

from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.class_dto import ClassCreateDTO, ClassUpdateDTO, ClassFilterDTO
from src.domain.view_models.class_view_model import ClassViewModel

class ClassService(BaseService):
    """Service for Class business logic"""
    
    def __init__(
        self,
        repository: ClassRepository,
        component_repo: CourseComponentRepository,
        user_class_repo: UserClassRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.component_repo = component_repo
        self.user_class_repo = user_class_repo
    
    async def create_class(self, dto: ClassCreateDTO) -> ClassViewModel:
        """Create a new class"""
        # Validate component exists and is active
        component = await self.component_repo.get_by_id(UUID(dto.component_id))
        if not component:
            raise ValueError("Component not found")
        if not component.active:
            raise ValueError("Component is not active")
        
        entity = DtoToEntityMapper.class_(dto)
        model = EntityToModelMapper.class_(entity)
        saved_model = await self.repository.create(model)
        saved_entity = ModelToEntityMapper.class_(saved_model)
        return EntityToViewModelMapper.class_(saved_entity)
    
    async def update_class(self, class_id: UUID, dto: ClassUpdateDTO) -> ClassViewModel:
        """Update a class"""
        model = await self.repository.get_by_id(class_id)
        if not model:
            raise ValueError("Class not found")
        
        entity = ModelToEntityMapper.class_(model)
        updated_entity = UpdateMapper.class_(entity, dto)
        updated_model = EntityToModelMapper.class_(updated_entity)
        saved_model = await self.repository.update(updated_model)
        saved_entity = ModelToEntityMapper.class_(saved_model)
        return EntityToViewModelMapper.class_(saved_entity)
    
    async def find_classes(self, filters: ClassFilterDTO) -> dict:
        """Find classes with filters"""
        skip = (filters.page - 1) * filters.page_size
        
        models = await self.repository.find_by_filters(
            component_id=UUID(filters.component_id) if filters.component_id else None,
            shift_type_id=filters.shift_type_id,
            active=filters.active,
            skip=skip,
            limit=filters.page_size
        )
        
        total = await self.repository.count({'active': filters.active})
        
        entities = [ModelToEntityMapper.class_(model) for model in models]
        view_models = [EntityToViewModelMapper.class_(entity) for entity in entities]
        
        return {
            'items': view_models,
            'total': total,
            'page': filters.page,
            'page_size': filters.page_size,
            'total_pages': (total + filters.page_size - 1) // filters.page_size
        }
    
    async def deactivate_class(self, class_id: UUID) -> bool:
        """Deactivate a class and all its active enrollments"""
        class_ = await self.repository.get_by_id(class_id)
        if not class_:
            raise ValueError("Class not found")
        
        if not class_.active:
            raise ValueError("Class already deactivated")
        
        # Get all active enrollments for this class
        active_enrollments = await self.user_class_repo.get_active_by_class_id(class_id)
        
        # Deactivate all enrollments and log the action
        for enrollment in active_enrollments:
            enrollment.active = False
            await self.user_class_repo.update(enrollment)
        
        # Deactivate the class
        result = await self.repository.deactivate(class_id)
        
        # Return summary
        return {
            'success': result,
            'class_id': class_id,
            'unenrolled_students': len(active_enrollments)
        }
    
    async def activate_class(self, class_id: UUID) -> bool:
        """Activate a class"""
        class_ = await self.repository.get_by_id(class_id)
        if not class_:
            raise ValueError("Class not found")
        
        if class_.active:
            raise ValueError("Class already active")
        
        # Check if component is active
        component = await self.component_repo.get_by_id(UUID(bytes=class_.component_id))
        if not component or not component.active:
            raise ValueError("Cannot activate class because component is inactive")
        
        return await self.repository.activate(class_id)
    
    async def get_available_seats(self, class_id: UUID) -> dict:
        """Get available seats for a class"""
        class_ = await self.repository.get_by_id(class_id)
        if not class_:
            raise ValueError("Class not found")
        
        component = await self.component_repo.get_by_id(UUID(bytes=class_.component_id))
        
        return {
            'class_id': class_id,
            'seats_in_use': class_.seats_in_use,
            'seat_limit': component.seat_limit_per_class if component else 0,
            'available_seats': component.seat_limit_per_class - class_.seats_in_use if component else 0
        }