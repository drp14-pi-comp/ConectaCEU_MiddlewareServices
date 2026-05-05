"""Class attendance service - business logic for attendance"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.class_attendance_repository import ClassAttendanceRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.student_absence_justification_repository import StudentAbsenceJustificationRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.application.services.base_service import BaseService
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.dtos.class_attendance_dto import BulkClassAttendanceCreateDTO
from src.domain.entities.class_attendance import ClassAttendance
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class ClassAttendanceService(BaseService):
    """Service for Class Attendance business logic"""
    
    def __init__(
        self, 
        repository: ClassAttendanceRepository,
        user_class_repo: UserClassRepository,
        class_repo: ClassRepository,
        component_repo: CourseComponentRepository,
        absence_justification_repo: StudentAbsenceJustificationRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.user_class_repo = user_class_repo
        self.class_repo = class_repo
        self.component_repo = component_repo
        self.absence_justification_repo = absence_justification_repo
    
    async def initialize_attendance_for_session(self, session_id: UUID) -> List[dict]:
        """Create attendance records for all enrolled students"""
        try:
            from src.data.repositories.class_session_repository import ClassSessionRepository
            
            # Get session to find class_id
            session_repo = ClassSessionRepository(self.repository.session)
            session = await session_repo.get_by_id(session_id)
            if not session:
                raise ValueError("Session not found")
            
            # Get all active enrollments for this class
            enrollments = await self.user_class_repo.get_active_by_class_id(session.class_id)
            
            # Create attendance records
            attendances = []
            for enrollment in enrollments:
                attendance = ClassAttendance(
                    id=uuid4(),
                    created_at=DateTimeHandler.now(),
                    updated_at=None,
                    attended=False,
                    user_id=enrollment.user_id,
                    class_session_id=session_id
                )
                attendances.append(attendance)
            
            # Bulk save
            models = [EntityToModelMapper.class_attendance(a) for a in attendances]
            saved_models = await self.repository.bulk_create(models)
            
            saved_entities = [ModelToEntityMapper.class_attendance(m) for m in saved_models]
            return [EntityToViewModelMapper.class_attendance(e) for e in saved_entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def take_attendance(self, dto: BulkClassAttendanceCreateDTO) -> dict:
        """Take attendance for a session"""
        try:
            # Validate session exists
            from src.data.repositories.class_session_repository import ClassSessionRepository
            session_repo = ClassSessionRepository(self.repository.session)
            session = await session_repo.get_by_id(UUID(dto.class_session_id))
            if not session:
                raise ValueError("Session not found")
            
            # Business rule: Can only take attendance on or after session date
            if session.date > DateTimeHandler.now():
                raise ValueError("Cannot take attendance before session date")
            
            updated_count = 0
            for user_id_str, attended in dto.attendance_list.items():
                user_id = UUID(user_id_str)
                attendance = await self.repository.get_by_user_and_session(
                    user_id, 
                    UUID(dto.class_session_id)
                )
                if attendance:
                    attendance.attended = attended
                    await self.repository.update(attendance)
                    updated_count += 1
            
            # Get summary
            summary = await self.repository.get_attendance_summary(UUID(dto.class_session_id))
            
            return {
                'session_id': dto.class_session_id,
                'updated_count': updated_count,
                'summary': summary
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_session_attendance(self, session_id: UUID) -> dict:
        try:
            """Get attendance for a session"""
            attendances = await self.repository.get_by_session_id(session_id)
            summary = await self.repository.get_attendance_summary(session_id)
            
            entities = [ModelToEntityMapper.class_attendance(a) for a in attendances]
            view_models = [EntityToViewModelMapper.class_attendance(e) for e in entities]
            
            return {
                'session_id': session_id,
                'attendances': view_models,
                'summary': summary
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_user_class_attendance(self, user_id: UUID, class_id: UUID) -> dict:
        """Get attendance summary for a user in a class"""
        try:
            return await self.repository.get_user_attendance_summary(user_id, class_id)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def mark_single_attendance(self, attendance_id: UUID, attended: bool) -> dict:
        """Mark a single attendance record"""
        try:
            attendance = await self.repository.get_by_id(attendance_id)
            if not attendance:
                raise ValueError("Attendance record not found")
            
            # Business rule: Can't modify attendance after 7 days
            from datetime import timedelta
            if attendance.created_at < DateTimeHandler.now() - timedelta(days=7):
                raise ValueError("Cannot modify attendance after 7 days")
            
            await self.repository.mark_attendance(attendance_id, attended)
            
            return {
                'attendance_id': attendance_id,
                'attended': attended,
                'updated_at': DateTimeHandler.now()
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        date: Optional[date] = None,
        attended: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """
        Get all sessions for a user with optional filters.
        Shows future sessions too (with attended = None).
        
        Args:
            user_id: User to get sessions for
            date: Optional filter by specific date
            attended: Optional filter by attendance status (None = all, including future)
            page: Page number
            page_size: Items per page
        
        Returns:
            Dict with paginated session list
        """
        try:
            from src.data.repositories.class_session_repository import ClassSessionRepository
            
            session_repo = ClassSessionRepository(self.repository.session)
            
            # Get all enrollments for the user
            enrollments = await self.user_class_repo.get_active_by_user_id(user_id)
            all_sessions = []
            
            for enrollment in enrollments:
                class_id = UUID(bytes=enrollment.class_id)
                
                # Get all sessions for this class
                if date:
                    # Filter by specific date
                    class_sessions = await session_repo.get_by_date_range(
                        class_id,
                        datetime.combine(date, datetime.min.time()),
                        datetime.combine(date, datetime.max.time())
                    )
                else:
                    # Get all sessions
                    class_sessions = await session_repo.get_by_class_id(class_id)
                
                for session in class_sessions:
                    session_id = UUID(bytes=session.id)
                    
                    # Get attendance for this session
                    attendance = await self.repository.get_by_user_and_session(user_id, session_id)
                    
                    # Determine attendance status
                    is_past = session.date < DateTimeHandler.now()
                    attendance_status = None  # Default for future sessions
                    
                    if attendance:
                        attendance_status = attendance.attended
                    elif is_past:
                        attendance_status = False  # Past session without attendance = absent
                    
                    # Apply attendance filter
                    if attended is not None:
                        if attended and attendance_status is not True:
                            continue
                        if not attended and attendance_status is not False:
                            continue
                    
                    all_sessions.append({
                        'session_id': session_id,
                        'date': session.date,
                        'class_id': class_id,
                        'attended': attendance_status,
                        'is_past': is_past,
                        'is_future': not is_past,
                        'attendance_id': UUID(bytes=attendance.id) if attendance else None
                    })
            
            # Sort by date
            all_sessions.sort(key=lambda s: s['date'], reverse=True)
            
            # Paginate
            skip = (page - 1) * page_size
            items = all_sessions[skip:skip + page_size]
            
            return {
                'items': items,
            }
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)

    async def submit_absence_justification(self, attendance_id: UUID, document_id: UUID, user_id: UUID) -> dict:
        """
        Student submits a justification document for an absence.
        """
        from uuid import uuid4
        from src.domain.entities.student_absence_justification import StudentAbsenceJustification
        from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
        
        # Verify the attendance record exists and belongs to this user
        attendance = await self.repository.get_by_id(attendance_id)
        if not attendance:
            raise ValueError("Attendance record not found")
        
        if UUID(bytes=attendance.user_id) != user_id:
            raise ValueError("This attendance record does not belong to you")
        
        # Verify the student was actually absent
        if attendance.attended:
            raise ValueError("Cannot justify an attendance that was present")
        
        # Check if justification already exists
        existing = await self.absence_justification_repo.get_by_attendance_id(attendance_id)
        if existing:
            if existing.document_id:
                raise ValueError("A justification has already been submitted for this absence")
            else:
                await self.absence_justification_repo.update_document_id(UUID(bytes=existing.id), document_id)
                return {
                    "message": "Justification document submitted successfully. Awaiting validation.",
                    "justification_id": str(UUID(bytes=existing.id)),
                    "document_id": str(document_id)
                }
        
        # Create new justification
        justification = StudentAbsenceJustification(
            id=uuid4(),
            created_at=DateTimeHandler.now(),
            class_attendance_id=attendance_id,
            document_id=document_id
        )
        
        justification_model = EntityToModelMapper.student_absence_justification(justification)
        saved = await self.absence_justification_repo.create(justification_model)
        
        return {
            "message": "Justification submitted successfully. Awaiting validation.",
            "justification_id": str(UUID(bytes=saved.id)),
            "document_id": str(document_id)
        }