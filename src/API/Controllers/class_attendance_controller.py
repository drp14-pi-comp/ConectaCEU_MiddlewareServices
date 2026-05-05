"""Class attendance controller"""
from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.application.services.class_attendance_service import ClassAttendanceService
from src.data.repositories.class_attendance_repository import ClassAttendanceRepository
from src.data.repositories.student_absence_justification_repository import StudentAbsenceJustificationRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.dtos.class_attendance_dto import BulkClassAttendanceCreateDTO
from src.domain.entities.user import User

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
    dependencies=[Depends(get_current_active_user)]
)


def get_attendance_service(db: Session = Depends(get_db)) -> ClassAttendanceService:
    repository = ClassAttendanceRepository(db)
    user_class_repo = UserClassRepository(db)
    class_repo = ClassRepository(db)
    component_repo = CourseComponentRepository(db)
    absence_justification_repo = StudentAbsenceJustificationRepository(db)
    return ClassAttendanceService(repository, user_class_repo, class_repo, component_repo, absence_justification_repo)


@router.post("/session/{session_id}/initialize")
async def initialize_attendance(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Initialize attendance records for a session. Educators (4) and Coordinators (3) only."""
    if current_user.user_type_id not in [3, 4]:
        raise HTTPException(status_code=403, detail="Only educators and coordinators can initialize attendance")
    
    try:
        return await service.initialize_attendance_for_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/take")
async def take_attendance(
    dto: BulkClassAttendanceCreateDTO,
    current_user: User = Depends(get_current_active_user),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Take attendance for a session. Educators (4) and Coordinators (3) only."""
    if current_user.user_type_id not in [3, 4]:
        raise HTTPException(status_code=403, detail="Only educators and coordinators can take attendance")
    
    try:
        return await service.take_attendance(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{attendance_id}")
async def mark_single_attendance(
    attendance_id: UUID,
    attended: bool,
    current_user: User = Depends(get_current_active_user),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Mark a single attendance record. Educators (4) and Coordinators (3) only."""
    if current_user.user_type_id not in [3, 4]:
        raise HTTPException(status_code=403, detail="Only educators and coordinators can mark attendance")
    
    try:
        return await service.mark_single_attendance(attendance_id, attended)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_attendance(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Get attendance for a session."""
    return await service.get_session_attendance(session_id)


@router.get("/user/{user_id}/class/{class_id}")
async def get_user_class_attendance(
    user_id: UUID,
    class_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Get attendance summary for a user in a class."""
    if current_user.user_type_id not in [3, 4] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own attendance")
    
    return await service.get_user_class_attendance(user_id, class_id)


@router.get("/user/{user_id}/sessions")
async def get_user_sessions(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    date: Optional[date] = Query(None),
    attended: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Get all sessions for a user with filters."""
    if current_user.user_type_id not in [3, 4] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own sessions")
    
    return await service.get_user_sessions(
        user_id=user_id,
        date=date,
        attended=attended,
        page=page,
        page_size=page_size
    )

@router.post("/{attendance_id}/justify")
async def submit_absence_justification(
    attendance_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """
    Submit a justification document for an absence.
    """
    try:
        return await service.submit_absence_justification(attendance_id, document_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))