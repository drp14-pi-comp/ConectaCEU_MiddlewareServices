"""Class session service - business logic for Class Session entity"""
from typing import List
from uuid import UUID
from datetime import datetime

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.dtos.class_session_dto import ClassSessionCreateDTO
from src.domain.view_models.class_session_view_model import ClassSessionViewModel
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class ClassSessionService(BaseService):
    """Service for Class Session business logic"""
    
    def __init__(self, repository: ClassSessionRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create_session(self, dto: ClassSessionCreateDTO) -> ClassSessionViewModel:
        """Create a new class session"""
        try:
            # Validate date is in the future
            if dto.date < DateTimeHandler.now():
                raise ValueError("Session date must be in the future")
            
            entity = DtoToEntityMapper.class_session(dto)
            model = EntityToModelMapper.class_session(entity)
            saved_model = await self.repository.create(model)
            saved_entity = ModelToEntityMapper.class_session(saved_model)
            return EntityToViewModelMapper.class_session(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_class_sessions(self, class_id: UUID) -> List[ClassSessionViewModel]:
        """Get all sessions for a class"""
        try:
            models = await self.repository.get_by_class_id(class_id)
            entities = [ModelToEntityMapper.class_session(model) for model in models]
            return [EntityToViewModelMapper.class_session(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_upcoming_sessions(self, class_id: UUID) -> List[ClassSessionViewModel]:
        """Get upcoming sessions for a class"""
        try:
            models = await self.repository.get_upcoming_sessions(class_id)
            entities = [ModelToEntityMapper.class_session(model) for model in models]
            return [EntityToViewModelMapper.class_session(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_past_sessions(self, class_id: UUID) -> List[ClassSessionViewModel]:
        """Get past sessions for a class"""
        try:
            models = await self.repository.get_past_sessions(class_id)
            entities = [ModelToEntityMapper.class_session(model) for model in models]
            return [EntityToViewModelMapper.class_session(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_sessions_by_date_range(
        self,
        class_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[ClassSessionViewModel]:
        """Get sessions within a date range"""
        try:
            models = await self.repository.get_by_date_range(class_id, start_date, end_date)
            entities = [ModelToEntityMapper.class_session(model) for model in models]
            return [EntityToViewModelMapper.class_session(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)