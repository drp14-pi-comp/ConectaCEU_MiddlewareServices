"""Class attendance service - business logic for attendance"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.models.document_validation_model import DocumentValidationModel
from src.data.repositories.class_attendance_repository import ClassAttendanceRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.document_repository import DocumentRepository
from src.data.repositories.student_absence_justification_repository import StudentAbsenceJustificationRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.application.services.base_service import BaseService
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.dtos.class_attendance_dto import BulkClassAttendanceCreateDTO
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class ClassAttendanceService(BaseService):
    """Service for Class Attendance business logic"""
    
    def __init__(
        self, 
        repository: ClassAttendanceRepository,
        user_class_repo: UserClassRepository,
        class_repo: ClassRepository,
        session_repo: ClassSessionRepository,
        component_repo: CourseComponentRepository,
        document_repo: DocumentRepository,
        absence_justification_repo: StudentAbsenceJustificationRepository
    ):
        super().__init__(repository, 'class_attendance', mapper_class=ModelToEntityMapper)
        self.repository = repository
        self.user_class_repo = user_class_repo
        self.class_repo = class_repo
        self.session_repo = session_repo
        self.component_repo = component_repo
        self.document_repo = document_repo
        self.absence_justification_repo = absence_justification_repo
    
    async def take_attendance(self, dto: BulkClassAttendanceCreateDTO) -> dict:
        """
        Takes attendance for a session in one go.
        Client sends the complete list of students with their status.
        Creates or updates attendance records directly.
        """
        session_id = UUID(dto.class_session_id)
        
        # Validate session exists
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Sessão não encontrada")
        
        # Validate session date
        if session.date.date() > DateTimeHandler.now().date():
            raise ValueError("Não é possível registrar chamada antes da data")
        
        created = 0
        updated = 0
        
        for entry in dto.attendances:
            user_id = UUID(entry.user_id)
            
            # Check if attendance record already exists
            existing = await self.repository.get_by_user_and_session(user_id, session_id)
            
            if existing:
                # Update existing record
                existing.attended = entry.attended
                await self.repository.update(existing)
                updated += 1
            else:
                # Create new record
                from uuid import uuid4
                from src.domain.entities.class_attendance import ClassAttendance
                
                attendance = ClassAttendance(
                    id=uuid4(),
                    created_at=DateTimeHandler.now(),
                    updated_at=None,
                    attended=entry.attended,
                    user_id=user_id,
                    class_session_id=session_id
                )
                model = EntityToModelMapper.class_attendance(attendance)
                await self.repository.create(model)
                created += 1
        
        self.repository.session.commit()
        summary = await self.repository.get_attendance_summary(session_id)
        
        return {
            'session_id': str(session_id),
            'created': created,
            'updated': updated,
            'summary': summary
        }
    
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
                    is_past = session.date.date() < DateTimeHandler.now().date()
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

    async def submit_absence_justification(self, attendance_id: UUID, document: DocumentCreateDTO, user_id: UUID) -> dict:
        """
        Student submits a justification document for an absence.
        """
        if user_id != UUID(document.user_id):
            raise ValueError('Você só pode enviar justificativas por si mesmo')

        from uuid import uuid4
        from src.domain.entities.student_absence_justification import StudentAbsenceJustification
        from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
        
        # Verify the attendance record exists and belongs to this user
        attendance = await self.repository.get_by_id(attendance_id)
        if not attendance:
            raise ValueError("Chamada não encontrada")
        
        if UUID(bytes=attendance.user_id) != user_id:
            raise ValueError("Esta chamada não pertence a você")
        
        # Verify the student was actually absent
        if attendance.attended:
            raise ValueError("Não é possível justificar uma chamada já com presença")
        
        # Check if justification already exists
        existing = await self.absence_justification_repo.get_by_attendance_id(attendance_id)
        if existing and existing.document_id:
            raise ValueError("Já existe uma justificativa para esta ausência")
        
        # Create the document first
        from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
        
        doc_entity = DtoToEntityMapper.document(document)
        doc_entity.user_id = user_id
        doc_model = EntityToModelMapper.document(doc_entity)
        saved_doc = await self.document_repo.create(doc_model)
        document_id = UUID(bytes=saved_doc.id)

        # Create document validation
        from src.data.repositories.document_validation_repository import DocumentValidationRepository
        doc_validation_repo = DocumentValidationRepository(self.repository.session)
        doc_validation = DocumentValidationModel(
            id=uuid4().bytes,
            created_at=DateTimeHandler.now(),
            updated_at=None,
            rejection_reason=None,
            document_validation_status_type_id=1,
            document_id=UUID(bytes=saved_doc.id)
        )
        await doc_validation_repo.create(doc_validation)
        
        # Create new justification
        justification = StudentAbsenceJustification(
            id=uuid4(),
            created_at=DateTimeHandler.now(),
            class_attendance_id=attendance_id,
            document_id=document_id
        )
        
        justification_model = EntityToModelMapper.student_absence_justification(justification)
        saved = await self.absence_justification_repo.create(justification_model)
        self.repository.session.commit()
        
        return {
            "message": "Justificativa carregada com sucesso. Aguarde validação.",
            "justification_id": str(UUID(bytes=saved.id)),
            "document_id": str(document_id)
        }