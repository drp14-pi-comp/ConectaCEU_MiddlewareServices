"""User class enrollment service - business logic for User Class entity"""
from typing import List, Optional
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
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
        super().__init__(repository, 'user_class', mapper_class=ModelToEntityMapper)
        self.repository = repository
        self.class_repo = class_repo
        self.class_session_repo = class_session_repo
    
    async def enroll_user(
        self,
        dto: UserClassEnrollDTO,
        enrolled_by_user_id: Optional[UUID] = None,
        user_ip_address: Optional[str] = None
    ) -> UserClassViewModel:
        """Enroll a user in a class with validation"""
        try:
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
                    self.repository.session.commit()
                    return EntityToViewModelMapper.user_class(saved_entity)
            
            # Validate enrollment limits and shift conflicts
            await self._validate_enrollment_rules(user_id, class_id)
            
            # Create new enrollment
            entity = DtoToEntityMapper.user_class(dto)
            model = EntityToModelMapper.user_class(entity)
            saved_model = await self.repository.create(model)
            
            # Increment seats in use
            await self.class_repo.increment_seats(class_id)

            if enrolled_by_user_id:
                from src.data.repositories.log_student_enrollment_repository import LogStudentEnrollmentRepository
                log_repo = LogStudentEnrollmentRepository(self.repository.session)
                course = await self._get_course_for_class(class_id)
                await log_repo.log(
                    enrolled=True,
                    user_id=enrolled_by_user_id.bytes,
                    user_ip_address=user_ip_address or "unknown",
                    course_id=course.id
                )
            
            self.repository.session.commit()
            
            saved_entity = ModelToEntityMapper.user_class(saved_model)
            return EntityToViewModelMapper.user_class(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def validate_bulk_enrollment(self, class_id: UUID, user_ids: List[str]) -> dict:
        """
        Validate if users can be enrolled in a class.
        Returns validation result with available seats and any issues.
        """
        try:
            class_ = await self.class_repo.get_by_id(class_id)
            if not class_:
                return {'valid': False, 'reason': 'Class not found'}
            
            if not class_.active:
                return {'valid': False, 'reason': 'Class is inactive'}
            
            component = await self._get_component_for_class(class_id)
            if not component:
                return {'valid': False, 'reason': 'Component not found'}
            
            available_seats = component.seat_limit_per_class - class_.seats_in_use
            requested = len(user_ids)
            
            if requested > available_seats:
                return {
                    'valid': False,
                    'reason': f'Insufficient seats',
                    'available_seats': available_seats,
                    'requested': requested
                }
            
            # Check each user
            issues = []
            for user_id in user_ids:
                try:
                    user_uuid = UUID(user_id)
                    existing = await self.repository.get_by_user_and_class(user_uuid, class_id)
                    if existing and existing.active:
                        issues.append({'user_id': user_id, 'issue': 'Already enrolled'})
                        continue
                    
                    try:
                        await self._validate_enrollment_rules(user_uuid, class_id)
                    except ValueError as e:
                        issues.append({'user_id': user_id, 'issue': str(e)})
                except ValueError:
                    issues.append({'user_id': user_id, 'issue': 'Invalid user ID format'})

            self.repository.session.commit()
            
            return {
                'valid': len(issues) == 0,
                'available_seats': available_seats,
                'requested': requested,
                'valid_enrollments': requested - len(issues),
                'issues': issues
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)

    async def bulk_enroll(self, dto: UserClassBulkEnrollDTO) -> dict:
        """Bulk enroll users after validation"""
        try:
            validation = await self.validate_bulk_enrollment(UUID(dto.class_id), dto.user_ids)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'class_id': dto.class_id,
                    'validation': validation,
                    'enrolled': [],
                    'failed': validation['issues']
                }
            
            enrolled = []
            for user_id in dto.user_ids:
                enroll_dto = UserClassEnrollDTO(user_id=user_id, class_id=dto.class_id)
                result = await self.enroll_user(enroll_dto)
                enrolled.append(result)
            
            self.repository.session.commit()
            
            return {
                'success': True,
                'class_id': dto.class_id,
                'enrolled_count': len(enrolled),
                'available_seats_remaining': validation['available_seats'] - len(enrolled),
                'enrolled': enrolled
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def unenroll_user(
        self,
        enrollment_id: UUID,
        unenrolled_by_user_id: Optional[UUID] = None,
        user_ip_address: Optional[str] = None
    ) -> bool:
        """Unenroll a user from a class"""
        try:
            enrollment = await self.repository.get_by_id(enrollment_id)
            if not enrollment:
                raise ValueError("Enrollment not found")
            
            if not enrollment.active:
                raise ValueError("Enrollment already inactive")
            
            result = await self.repository.deactivate_enrollment(enrollment_id)
            
            if result:
                # Decrement seats in use
                await self.class_repo.decrement_seats(UUID(bytes=enrollment.class_id))

            if unenrolled_by_user_id:
                from src.data.repositories.log_student_enrollment_repository import LogStudentEnrollmentRepository
                log_repo = LogStudentEnrollmentRepository(self.repository.session)
                class_id = UUID(bytes=enrollment.class_id)
                course = await self._get_course_for_class(class_id)
                await log_repo.log(
                    enrolled=False,
                    user_id=unenrolled_by_user_id.bytes,
                    user_ip_address=user_ip_address or "unknown",
                    course_id=course.id
                )

            self.repository.session.commit()
            
            return result
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_user_enrollments(self, user_id: UUID) -> List[UserClassViewModel]:
        """Get all enrollments for a user"""
        try:
            models = await self.repository.get_by_user_id(user_id)
            entities = [ModelToEntityMapper.user_class(model) for model in models]
            return [EntityToViewModelMapper.user_class(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_user_active_enrollments_with_details(self, user_id: UUID) -> List[dict]:
        """Get user's active enrollments with class and shift details"""
        try:
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
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_class_enrollments(self, class_id: UUID) -> List[UserClassViewModel]:
        """Get all enrollments for a class"""
        try:
            models = await self.repository.get_by_class_id(class_id)
            entities = [ModelToEntityMapper.user_class(model) for model in models]
            return [EntityToViewModelMapper.user_class(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_active_class_enrollments(self, class_id: UUID) -> List[UserClassViewModel]:
        """Get active enrollments for a class"""
        try:
            models = await self.repository.get_active_by_class_id(class_id)
            entities = [ModelToEntityMapper.user_class(model) for model in models]
            return [EntityToViewModelMapper.user_class(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
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
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_enrollment_summary(self, user_id: UUID) -> dict:
        """Get enrollment summary for a user"""
        try:
            active_enrollments = await self.get_user_active_enrollments_with_details(user_id)
            
            shifts_enrolled = set()
            for enrollment in active_enrollments:
                shifts_enrolled.add(enrollment['shift_type_id'])
            
            shift_names = {1: "Manhã", 2: "Tarde", 3: "Noite"}
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
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def _validate_enrollment_rules(self, user_id: UUID, new_class_id: UUID) -> None:
        """
        Validate enrollment business rules:
        1. Maximum 3 enrollments per user
        2. Cannot enroll in multiple classes with the same shift
        """
        try:
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
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def _get_component_for_class(self, class_id: UUID):
        """Get the component for a class"""
        try:
            from src.data.repositories.course_component_repository import CourseComponentRepository
            
            class_ = await self.class_repo.get_by_id(class_id)
            if class_:
                component_repo = CourseComponentRepository(self.class_repo.session)
                component = await component_repo.get_by_id(UUID(bytes=class_.component_id))
                return component
            return None
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    

    async def _get_course_for_class(self, class_id: UUID):
        """Get the course for a class"""
        try:
            from src.data.repositories.course_repository import CourseRepository
            
            class_ = await self.class_repo.get_by_id(class_id)
            if class_:
                component = await self._get_component_for_class(class_id)
                course_repo = CourseRepository(self.class_repo.session)
                course = await course_repo.get_by_id(UUID(bytes=component.course_id))
                return course
            return None
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)