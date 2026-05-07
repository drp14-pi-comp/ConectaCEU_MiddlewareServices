"""Class service - business logic for Class entity"""
from datetime import date, datetime
from typing import List
from uuid import UUID, uuid4

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.class_dto import ClassBulkCreateDTO, ClassCreateDTO, ClassUpdateDTO, ClassFilterDTO
from src.domain.entities.class_ import Class
from src.domain.entities.class_session import ClassSession
from src.domain.view_models.class_view_model import ClassViewModel
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class ClassService(BaseService):
    """Service for Class business logic"""
    
    def __init__(
        self,
        repository: ClassRepository,
        component_repo: CourseComponentRepository,
        user_class_repo: UserClassRepository,
        course_repo: CourseRepository,
        class_session_repo: ClassSessionRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.component_repo = component_repo
        self.user_class_repo = user_class_repo
        self.course_repo = course_repo
        self.class_session_repo = class_session_repo
    
    async def create_class(self, dto: ClassCreateDTO) -> ClassViewModel:
        """Create a new class"""
        try:
            # Validate component exists and is active
            component = await self.component_repo.get_by_id(UUID(dto.component_id))
            if not component:
                raise ValueError("Component not found")
            if not component.active:
                raise ValueError("Component is not active")
            
            entity = DtoToEntityMapper.class_(dto)
            model = EntityToModelMapper.class_(entity)
            saved_model = await self.repository.create(model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.class_(saved_model)
            return EntityToViewModelMapper.class_(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def bulk_create_classes_with_sessions(self, dto: ClassBulkCreateDTO) -> dict:
        """
        Create multiple classes (one per shift) with sessions based on date range.
        This handles the form submission from the class/session creation page.
        """
        try:
            course_id = UUID(dto.course_id)
            component_id = UUID(dto.course_component_id)
            
            # Validate course exists
            course = await self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found")
            
            # Validate component exists and belongs to course
            component = await self.component_repo.get_by_id(component_id)
            if not component:
                raise ValueError("Component not found")
            if UUID(bytes=component.course_id) != course_id:
                raise ValueError("Component does not belong to this course")
            
            # Validate component is active
            if not component.active:
                raise ValueError("Component is not active")
            
            # Validate seat limits against component
            if dto.total_seat_limit_per_class > component.seat_limit_per_class:
                raise ValueError(
                    f"Total seat limit ({dto.total_seat_limit_per_class}) "
                    f"exceeds component seat limit ({component.seat_limit_per_class})"
                )
            
            # Generate session dates based on date range and days of week
            session_dates = self._generate_session_dates(
                dto.start_date,
                dto.end_date,
                dto.days_of_week
            )
            
            if not session_dates:
                raise ValueError("No valid session dates found in the given range and days")
            
            created_classes = []
            created_sessions = []
            
            # Create one class per shift type
            for shift_type_id in dto.shift_type_ids:
                # Create the class
                class_entity = Class(
                    id=uuid4(),
                    created_at=DateTimeHandler.now(),
                    updated_at=None,
                    seats_in_use=0,
                    active=True,
                    component_id=component_id,
                    shift_type_id=shift_type_id
                )
                
                class_model = EntityToModelMapper.class_(class_entity)
                saved_class = await self.repository.create(class_model)
                class_id = UUID(bytes=saved_class.id)
                
                class_info = {
                    'class_id': class_id,
                    'shift_type_id': shift_type_id,
                    'total_seats': dto.total_seat_limit_per_class,
                    'enrollment_limit': dto.enrollment_seat_limit,
                    'sessions_created': 0
                }
                
                # Create sessions for this class
                for session_date in session_dates:
                    session_entity = ClassSession(
                        id=uuid4(),
                        created_at=DateTimeHandler.now(),
                        updated_at=None,
                        date=datetime.combine(session_date, datetime.min.time()),
                        class_id=class_id
                    )
                    
                    session_model = EntityToModelMapper.class_session(session_entity)
                    saved_session = await self.class_session_repo.create(session_model)
                    
                    created_sessions.append({
                        'session_id': UUID(bytes=saved_session.id),
                        'date': session_date.isoformat(),
                        'class_id': class_id
                    })
                    
                    class_info['sessions_created'] += 1
                
                created_classes.append(class_info)

            self.repository.session.commit()
            
            return {
                'course_id': course_id,
                'component_id': component_id,
                'component_name': component.name,
                'total_classes_created': len(created_classes),
                'total_sessions_created': len(created_sessions),
                'session_dates': [d.isoformat() for d in session_dates],
                'classes': created_classes,
                'sessions': created_sessions
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def update_class(self, class_id: UUID, dto: ClassUpdateDTO) -> ClassViewModel:
        """Update a class"""
        try:
            model = await self.repository.get_by_id(class_id)
            if not model:
                raise ValueError("Class not found")
            
            entity = ModelToEntityMapper.class_(model)
            updated_entity = UpdateMapper.class_(entity, dto)
            updated_model = EntityToModelMapper.class_(updated_entity)
            saved_model = await self.repository.update(updated_model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.class_(saved_model)
            return EntityToViewModelMapper.class_(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def find_classes(self, filters: ClassFilterDTO) -> dict:
        """Find classes with filters"""
        try:
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
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def deactivate_class(self, class_id: UUID) -> bool:
        """Deactivate a class and all its active enrollments"""
        try:
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
            self.repository.session.commit()
            
            # Return summary
            return {
                'success': result,
                'class_id': class_id,
                'unenrolled_students': len(active_enrollments)
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def activate_class(self, class_id: UUID) -> bool:
        """Activate a class"""
        try:
            class_ = await self.repository.get_by_id(class_id)
            if not class_:
                raise ValueError("Class not found")
            
            if class_.active:
                raise ValueError("Class already active")
            
            # Check if component is active
            component = await self.component_repo.get_by_id(UUID(bytes=class_.component_id))
            if not component or not component.active:
                raise ValueError("Cannot activate class because component is inactive")
            
            result = await self.repository.activate(class_id)
            self.repository.session.commit()
            
            return result
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_available_seats(self, class_id: UUID) -> dict:
        """Get available seats for a class"""
        try:
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
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)

    def _generate_session_dates(
        self,
        start_date: date,
        end_date: date,
        days_of_week: List[int]
    ) -> List[date]:
        """
        Generate session dates within a range for specific days of week.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            days_of_week: List of days (0=Monday, 6=Sunday)
        
        Returns:
            List of dates that match the criteria
        """
        from datetime import timedelta
        
        session_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                session_dates.append(current_date)
            current_date += timedelta(days=1)
        
        return session_dates