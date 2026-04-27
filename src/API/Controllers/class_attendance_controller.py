"""Class attendance controller"""
from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.services.class_attendance_service import ClassAttendanceService
from src.data.repositories.class_attendance_repository import ClassAttendanceRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.db_context.database import get_db
from src.domain.dtos.class_attendance_dto import (ClassAttendanceCreateDTO, ClassAttendanceUpdateDTO, BulkClassAttendanceCreateDTO)
from src.domain.view_models.class_attendance_view_model import ClassAttendanceViewModel

router = APIRouter(prefix="/attendance", tags=["Attendance"])

def get_attendance_service(db: Session = Depends(get_db)) -> ClassAttendanceService:
    repository = ClassAttendanceRepository(db)
    user_class_repo = UserClassRepository(db)
    return ClassAttendanceService(repository, user_class_repo)

@router.post("/session/{session_id}/initialize")
async def initialize_attendance(
    session_id: UUID,
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Initialize attendance records for a session"""
    try:
        return await service.initialize_attendance_for_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/take")
async def take_attendance(
    dto: BulkClassAttendanceCreateDTO,
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Take attendance for a session"""
    try:
        return await service.take_attendance(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_attendance(
    session_id: UUID,
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Get attendance for a session"""
    return await service.get_session_attendance(session_id)

@router.get("/user/{user_id}/class/{class_id}")
async def get_user_class_attendance(
    user_id: UUID,
    class_id: UUID,
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Get attendance summary for a user in a class"""
    return await service.get_user_class_attendance(user_id, class_id)

@router.patch("/{attendance_id}")
async def mark_single_attendance(
    attendance_id: UUID,
    attended: bool,
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """Mark a single attendance record"""
    try:
        return await service.mark_single_attendance(attendance_id, attended)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/user/{user_id}/sessions")
async def get_user_sessions(
    user_id: UUID,
    date: Optional[date] = Query(None, description="Filter by specific date"),
    attended: Optional[bool] = Query(None, description="Filter by attendance status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: ClassAttendanceService = Depends(get_attendance_service)
):
    """
    Get all sessions for a user with filters.
    
    - Shows past sessions with attendance status
    - Shows future sessions with attendance = null
    - Filter by date and/or attendance status
    """
    return await service.get_user_sessions(
        user_id=user_id,
        date=date,
        attended=attended,
        page=page,
        page_size=page_size
    )