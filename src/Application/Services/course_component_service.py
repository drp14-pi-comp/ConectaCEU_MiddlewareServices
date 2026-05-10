"""Course component service - business logic for Course Component entity"""
from typing import List
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.course_component_dto import CourseComponentCreateDTO, CourseComponentUpdateDTO
from src.domain.view_models.course_component_view_model import CourseComponentViewModel

class CourseComponentService(BaseService):
    """Service for Course Component business logic"""
    
    def __init__(self, repository: CourseComponentRepository):
        super().__init__(repository, 'course_component', mapper_class=ModelToEntityMapper)
        self.repository = repository
    
    async def create_component(self, dto: CourseComponentCreateDTO) -> CourseComponentViewModel:
        """Create a new course component"""
        try:
            if not dto.course_id:
                raise ValueError("ID do curso é obrigatório")

            component_exists = await self.repository.component_exists(dto.name, UUID(dto.course_id))
            if component_exists:
                raise ValueError("Componente já existe para este curso")
            
            entity = DtoToEntityMapper.course_component(dto)
            model = EntityToModelMapper.course_component(entity)
            model.active = True
            saved_model = await self.repository.create(model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.course_component(saved_model)
            return EntityToViewModelMapper.course_component(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def update_component(self, component_id: UUID, dto: CourseComponentUpdateDTO) -> CourseComponentViewModel:
        """Update a course component"""
        try:
            model = await self.repository.get_by_id(component_id)
            if not model:
                raise ValueError("Componente não encontrado")
            
            if dto.name:
                component_exists = await self.repository.component_exists(dto.name, UUID(dto.course_id))
                if component_exists and component_exists.id != model.id:
                    raise ValueError("Componente já existe para este curso")
            
            entity = ModelToEntityMapper.course_component(model)
            updated_entity = UpdateMapper.course_component(entity, dto)
            updated_model = EntityToModelMapper.course_component(updated_entity)
            saved_model = await self.repository.update(updated_model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.course_component(saved_model)
            return EntityToViewModelMapper.course_component(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_course_components(self, course_id: UUID) -> List[CourseComponentViewModel]:
        """Get all components for a course"""
        try:
            models = await self.repository.get_by_course_id(course_id)
            entities = [ModelToEntityMapper.course_component(model) for model in models]
            return [EntityToViewModelMapper.course_component(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def deactivate_component(self, component_id: UUID) -> bool:
        """Deactivate a component"""
        try:
            component = await self.repository.get_by_id(component_id)
            if not component:
                raise ValueError("Componente não encontrado")
            
            if not component.active:
                raise ValueError("Componente já desativado")
            
            result = await self.repository.deactivate(component_id)
            self.repository.session.commit()
            
            return result
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def activate_component(self, component_id: UUID) -> bool:
        """Activate a component"""
        try:
            component = await self.repository.get_by_id(component_id)
            if not component:
                raise ValueError("Componente não encontrado")
            
            if not component.active:
                raise ValueError("Componente já ativo")
            
            result = await self.repository.activate(component_id)
            self.repository.session.commit()
            
            return result
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)