"""Class attendance service - business logic for attendance"""
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from src.data.repositories.class_attendance_repository import ClassAttendanceRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.dtos.class_attendance_dto import ClassAttendanceCreateDTO, BulkAttendanceCreateDTO
from src.domain.entities.class_attendance import ClassAttendance

class ClassAttendanceService(BaseService):
    """Service for Class Attendance business logic"""
    
    def __init__(
        self, 
        repository: ClassAttendanceRepository,
        user_class_repo: UserClassRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.user_class_repo = user_class_repo
    
    async def initialize_attendance_for_session(self, session_id: UUID) -> List[dict]:
        """Create attendance records for all enrolled students"""
        from src.data.models.class_session_model import ClassSession
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
                created_at=datetime.now(datetime.timezone.utc),
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
    
    async def take_attendance(self, dto: BulkAttendanceCreateDTO) -> dict:
        """Take attendance for a session"""
        # Validate session exists
        from src.data.repositories.class_session_repository import ClassSessionRepository
        session_repo = ClassSessionRepository(self.repository.session)
        session = await session_repo.get_by_id(UUID(dto.class_session_id))
        if not session:
            raise ValueError("Session not found")
        
        # Business rule: Can only take attendance on or after session date
        if session.date > datetime.now(datetime.timezone.utc):
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
    
    async def get_session_attendance(self, session_id: UUID) -> dict:
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
    
    async def get_user_class_attendance(self, user_id: UUID, class_id: UUID) -> dict:
        """Get attendance summary for a user in a class"""
        return await self.repository.get_user_attendance_summary(user_id, class_id)
    
    async def mark_single_attendance(self, attendance_id: UUID, attended: bool) -> dict:
        """Mark a single attendance record"""
        attendance = await self.repository.get_by_id(attendance_id)
        if not attendance:
            raise ValueError("Attendance record not found")
        
        # Business rule: Can't modify attendance after 7 days
        from datetime import timedelta
        if attendance.created_at < datetime.now(datetime.timezone.utc) - timedelta(days=7):
            raise ValueError("Cannot modify attendance after 7 days")
        
        await self.repository.mark_attendance(attendance_id, attended)
        
        return {
            'attendance_id': attendance_id,
            'attended': attended,
            'updated_at': datetime.now(datetime.timezone.utc)
        }