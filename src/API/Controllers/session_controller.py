"""Class session controller"""
from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.application.services.class_session_service import ClassSessionService
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.dtos.class_session_dto import ClassSessionCreateDTO
from src.domain.view_models.class_session_view_model import ClassSessionViewModel
from src.domain.entities.user import User

router = APIRouter(
    prefix="/session",
    tags=["Session"],
    dependencies=[Depends(get_current_active_user)]
)


def get_session_service(db: Session = Depends(get_db)) -> ClassSessionService:
    """Dependency injection for ClassSessionService"""
    repository = ClassSessionRepository(db)
    return ClassSessionService(repository)


@router.post("/", response_model=ClassSessionViewModel, status_code=status.HTTP_201_CREATED)
async def create_session(
    dto: ClassSessionCreateDTO,
    current_user: User = Depends(get_current_active_user),
    service: ClassSessionService = Depends(get_session_service)
):
    """Create a new class session. Admin (1), Coordinator (3), Educator (4) only."""
    if current_user.user_type_id not in [1, 3, 4]:
        raise HTTPException(status_code=403, detail="Only admins, coordinators, and educators can create sessions")
    
    try:
        return await service.create_session(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/class/{class_id}", response_model=List[ClassSessionViewModel])
async def get_class_sessions(
    class_id: UUID,
    service: ClassSessionService = Depends(get_session_service)
):
    """Get all sessions for a class."""
    return await service.get_class_sessions(class_id)


@router.get("/class/{class_id}/upcoming", response_model=List[ClassSessionViewModel])
async def get_upcoming_sessions(
    class_id: UUID,
    service: ClassSessionService = Depends(get_session_service)
):
    """Get upcoming sessions for a class."""
    return await service.get_upcoming_sessions(class_id)


@router.get("/class/{class_id}/past", response_model=List[ClassSessionViewModel])
async def get_past_sessions(
    class_id: UUID,
    service: ClassSessionService = Depends(get_session_service)
):
    """Get past sessions for a class."""
    return await service.get_past_sessions(class_id)


@router.get("/class/{class_id}/range", response_model=List[ClassSessionViewModel])
async def get_sessions_by_date_range(
    class_id: UUID,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    service: ClassSessionService = Depends(get_session_service)
):
    """Get sessions within a date range."""
    return await service.get_sessions_by_date_range(class_id, start_date, end_date)


@router.get("/{session_id}", response_model=ClassSessionViewModel)
async def get_session(
    session_id: UUID,
    service: ClassSessionService = Depends(get_session_service)
):
    """Get session by ID."""
    session = await service.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session