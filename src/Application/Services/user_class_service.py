"""User class enrollment service - business logic for User Class entity"""
from typing import List
from uuid import UUID

from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.dtos.user_class_dto import UserClassEnrollDTO, UserClassBulkEnrollDTO
from src.domain.view_models.user_class_view_model import UserClassViewModel

class UserClassService(BaseService):
    """Service for User Class enrollment business logic"""
    
    def __init__(
        self,
        repository: UserClassRepository,
        class_repo: ClassRepository,
        class_session_repo: ClassSessionRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.class_repo = class_repo
        self.class_session_repo = class_session_repo
    
    async def enroll_user(self, dto: UserClassEnrollDTO) -> UserClassViewModel:
        """Enroll a user in a class with validation"""
        user_id = UUID(dto.user_id)
        class_id = UUID(dto.class_id)
        
        # Check if already enrolled
        existing = await self.repository.get_by_user_and_class(user_id, class_id)
        if existing:
            if existing.active:
                raise ValueError("User already enrolled in this class")
            else:
                # Reactivate enrollment
                existing.active = True
                saved_model = await self.repository.update(existing)
                saved_entity = ModelToEntityMapper.user_class(saved_model)
                return EntityToViewModelMapper.user_class(saved_entity)
        
        # Validate enrollment limits and shift conflicts
        await self._validate_enrollment_rules(user_id, class_id)
        
        # Create new enrollment
        entity = DtoToEntityMapper.user_class(dto)
        model = EntityToModelMapper.user_class(entity)
        saved_model = await self.repository.create(model)
        
        # Increment seats in use
        await self.class_repo.increment_seats(class_id)
        
        saved_entity = ModelToEntityMapper.user_class(saved_model)
        return EntityToViewModelMapper.user_class(saved_entity)
    
    async def _validate_enrollment_rules(self, user_id: UUID, new_class_id: UUID) -> None:
        """
        Validate enrollment business rules:
        1. Maximum 3 enrollments per user
        2. Cannot enroll in multiple classes with the same shift
        """
        # Get user's active enrollments
        active_enrollments = await self.repository.get_active_by_user_id(user_id)
        
        # Rule 1: Maximum 3 enrollments
        if len(active_enrollments) >= 3:
            raise ValueError("User already enrolled in 3 classes (maximum limit reached)")
        
        # Get the shift of the new class
        new_class = await self.class_repo.get_by_id(new_class_id)
        if not new_class:
            raise ValueError("Class not found")
        
        if not new_class.active:
            raise ValueError("Cannot enroll in an inactive class")
        
        new_class_shift = new_class.shift_type_id
        
        # Rule 2: Check for shift conflicts with existing enrollments
        for enrollment in active_enrollments:
            existing_class = await self.class_repo.get_by_id(UUID(bytes=enrollment.class_id))
            if existing_class and existing_class.shift_type_id == new_class_shift:
                shift_names = {1: "morning", 2: "afternoon", 3: "evening"}
                shift_name = shift_names.get(new_class_shift, "same")
                raise ValueError(f"User already enrolled in a {shift_name} shift class")
        
        # Check if class has available seats
        component = await self._get_component_for_class(new_class_id)
        if component:
            if new_class.seats_in_use >= component.seat_limit_per_class:
                raise ValueError("Class has no available seats")
    
    async def _get_component_for_class(self, class_id: UUID):
        """Get the component for a class"""
        from src.data.repositories.course_component_repository import CourseComponentRepository
        
        class_ = await self.class_repo.get_by_id(class_id)
        if class_:
            # You would need ComponentRepository injected
            # This is a simplified version
            return None
        return None
    
    async def bulk_enroll(self, dto: UserClassBulkEnrollDTO) -> dict:
        """Bulk enroll users in a class"""
        enrolled = []
        failed = []
        
        for user_id in dto.user_ids:
            try:
                enroll_dto = UserClassEnrollDTO(user_id=user_id, class_id=dto.class_id)
                result = await self.enroll_user(enroll_dto)
                enrolled.append(result)
            except Exception as e:
                failed.append({'user_id': user_id, 'error': str(e)})
        
        return {
            'class_id': dto.class_id,
            'enrolled_count': len(enrolled),
            'failed_count': len(failed),
            'enrolled': enrolled,
            'failed': failed
        }
    
    async def unenroll_user(self, enrollment_id: UUID) -> bool:
        """Unenroll a user from a class"""
        enrollment = await self.repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")
        
        if not enrollment.active:
            raise ValueError("Enrollment already inactive")
        
        result = await self.repository.deactivate_enrollment(enrollment_id)
        
        if result:
            # Decrement seats in use
            await self.class_repo.decrement_seats(UUID(bytes=enrollment.class_id))
        
        return result
    
    async def get_user_enrollments(self, user_id: UUID) -> List[UserClassViewModel]:
        """Get all enrollments for a user"""
        models = await self.repository.get_by_user_id(user_id)
        entities = [ModelToEntityMapper.user_class(model) for model in models]
        return [EntityToViewModelMapper.user_class(entity) for entity in entities]
    
    async def get_user_active_enrollments_with_details(self, user_id: UUID) -> List[dict]:
        """Get user's active enrollments with class and shift details"""
        active_enrollments = await self.repository.get_active_by_user_id(user_id)
        
        enrollments_with_details = []
        for enrollment in active_enrollments:
            class_ = await self.class_repo.get_by_id(UUID(bytes=enrollment.class_id))
            if class_:
                enrollments_with_details.append({
                    'enrollment_id': UUID(bytes=enrollment.id),
                    'class_id': UUID(bytes=class_.id),
                    'shift_type_id': class_.shift_type_id,
                    'enrolled_at': enrollment.created_at
                })
        
        return enrollments_with_details
    
    async def get_class_enrollments(self, class_id: UUID) -> List[UserClassViewModel]:
        """Get all enrollments for a class"""
        models = await self.repository.get_by_class_id(class_id)
        entities = [ModelToEntityMapper.user_class(model) for model in models]
        return [EntityToViewModelMapper.user_class(entity) for entity in entities]
    
    async def get_active_class_enrollments(self, class_id: UUID) -> List[UserClassViewModel]:
        """Get active enrollments for a class"""
        models = await self.repository.get_active_by_class_id(class_id)
        entities = [ModelToEntityMapper.user_class(model) for model in models]
        return [EntityToViewModelMapper.user_class(entity) for entity in entities]
    
    async def check_enrollment_eligibility(self, user_id: UUID, class_id: UUID) -> dict:
        """
        Check if a user can enroll in a class without actually enrolling.
        Returns eligibility status and any restriction reasons.
        """
        try:
            await self._validate_enrollment_rules(user_id, class_id)
            
            # Check available seats
            class_ = await self.class_repo.get_by_id(class_id)
            component = await self._get_component_for_class(class_id)
            
            available_seats = 0
            if component and class_:
                available_seats = component.seat_limit_per_class - class_.seats_in_use
            
            return {
                'eligible': True,
                'restrictions': [],
                'available_seats': available_seats,
                'current_enrollments': len(await self.repository.get_active_by_user_id(user_id))
            }
        except ValueError as e:
            return {
                'eligible': False,
                'restrictions': [str(e)],
                'available_seats': 0,
                'current_enrollments': len(await self.repository.get_active_by_user_id(user_id))
            }
    
    async def get_enrollment_summary(self, user_id: UUID) -> dict:
        """Get enrollment summary for a user"""
        active_enrollments = await self.get_user_active_enrollments_with_details(user_id)
        
        shifts_enrolled = set()
        for enrollment in active_enrollments:
            shifts_enrolled.add(enrollment['shift_type_id'])
        
        shift_names = {1: "morning", 2: "afternoon", 3: "evening"}
        enrolled_shifts = [shift_names.get(s, f"shift_{s}") for s in shifts_enrolled]
        
        return {
            'user_id': user_id,
            'total_enrollments': len(active_enrollments),
            'max_enrollments': 3,
            'remaining_slots': 3 - len(active_enrollments),
            'enrolled_shifts': enrolled_shifts,
            'available_shifts': [s for s in shift_names.values() if s not in enrolled_shifts],
            'enrollments': active_enrollments
        }