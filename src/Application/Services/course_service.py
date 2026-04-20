"""Course service - business logic for Course entity"""
from typing import Optional
from uuid import UUID

from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.course_dto import CourseCreateDTO, CourseUpdateDTO
from src.domain.view_models.course_view_model import CourseViewModel

class CourseService(BaseService):
    """Service for Course business logic"""
    
    def __init__(
        self, 
        repository: CourseRepository,
        component_repo: CourseComponentRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.component_repo = component_repo
    
    async def create_course(self, dto: CourseCreateDTO) -> CourseViewModel:
        """Create a new course with validation"""
        # Check if name already exists
        existing = await self.repository.get_by_name(dto.name)
        if existing:
            raise ValueError("Course name already exists")
        
        # Convert DTO -> Entity
        entity = DtoToEntityMapper.course(dto)
        
        # Business rule: Validate workload
        if entity.workload < 10:
            raise ValueError("Course workload must be at least 10 hours")
        
        # Convert Entity -> Model and save
        model = EntityToModelMapper.course(entity)
        saved_model = await self.repository.create(model)
        
        # Convert back to ViewModel
        saved_entity = ModelToEntityMapper.course(saved_model)
        return EntityToViewModelMapper.course(saved_entity)
    
    async def update_course(self, course_id: UUID, dto: CourseUpdateDTO) -> CourseViewModel:
        """Update course with validation"""
        model = await self.repository.get_by_id(course_id)
        if not model:
            raise ValueError("Course not found")
        
        # Check name uniqueness if being updated
        if dto.name:
            existing = await self.repository.get_by_name(dto.name)
            if existing and existing.id != model.id:
                raise ValueError("Course name already exists")
        
        # Convert to entity and apply updates
        entity = ModelToEntityMapper.course(model)
        updated_entity = UpdateMapper.course(entity, dto)
        
        # Save changes
        updated_model = EntityToModelMapper.course(updated_entity)
        saved_model = await self.repository.update(updated_model)
        
        saved_entity = ModelToEntityMapper.course(saved_model)
        return EntityToViewModelMapper.course(saved_entity)
    
    async def deactivate_course(self, course_id: UUID) -> bool:
        """Deactivate a course, its components, and classes"""
        course = await self.repository.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        
        if not course.active:
            raise ValueError("Course already deactivated")
        
        # Get all components for this course
        components = await self.component_repo.get_by_course_id(course_id)
        
        for component in components:
            if component.active:
                # Get all classes for this component
                classes = await self.class_repo.get_by_component_id(UUID(bytes=component.id))
                
                for class_ in classes:
                    if class_.active:
                        # Deactivate all enrollments for this class
                        active_enrollments = await self.user_class_repo.get_active_by_class_id(UUID(bytes=class_.id))
                        for enrollment in active_enrollments:
                            enrollment.active = False
                            await self.user_class_repo.update(enrollment)
                        
                        # Deactivate the class
                        await self.class_repo.deactivate(UUID(bytes=class_.id))
                
                # Deactivate the component
                await self.component_repo.deactivate(UUID(bytes=component.id))
        
        # Deactivate the course
        return await self.repository.deactivate(course_id)
    
    async def activate_course(self, course_id: UUID) -> bool:
        """Activate course"""
        course = await self.repository.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        
        if course.active:
            raise ValueError("Course already active")
        
        return await self.repository.activate(course_id)
    
    async def find_courses(
        self,
        name: Optional[str] = None,
        active: Optional[bool] = None,
        educator_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """Find courses with filters"""
        skip = (page - 1) * page_size
        
        models = await self.repository.find_by_filters(
            name=name,
            active=active,
            educator_id=educator_id,
            skip=skip,
            limit=page_size
        )
        
        total = await self.repository.count({'active': active})
        
        entities = [ModelToEntityMapper.course(model) for model in models]
        view_models = [EntityToViewModelMapper.course(entity) for entity in entities]
        
        return {
            'items': view_models,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    async def get_course_with_components(self, course_id: UUID) -> dict:
        """Get course with its components"""
        course_model = await self.repository.get_by_id(course_id)
        if not course_model:
            raise ValueError("Course not found")
        
        components = await self.component_repo.get_by_course_id(course_id)
        
        course_entity = ModelToEntityMapper.course(course_model)
        component_entities = [ModelToEntityMapper.course_component(c) for c in components]
        
        return {
            'course': EntityToViewModelMapper.course(course_entity),
            'components': [EntityToViewModelMapper.course_component(c) for c in component_entities]
        }