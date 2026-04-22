"""User class enrollment controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.user_class_service import UserClassService
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.data.db_context.database import get_db
from src.domain.dtos.user_class_dto import UserClassEnrollDTO, UserClassBulkEnrollDTO
from src.domain.view_models.user_class_view_model import UserClassViewModel

router = APIRouter(prefix="/enrollment", tags=["Enrollment"])

def get_user_class_service(db: Session = Depends(get_db)) -> UserClassService:
    repository = UserClassRepository(db)
    class_repo = ClassRepository(db)
    session_repo = ClassSessionRepository(db)
    return UserClassService(repository, class_repo, session_repo)

@router.post("/", response_model=UserClassViewModel, status_code=status.HTTP_201_CREATED)
async def enroll_user(
    dto: UserClassEnrollDTO,
    service: UserClassService = Depends(get_user_class_service)
):
    """Enroll a user in a class"""
    try:
        return await service.enroll_user(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk")
async def bulk_enroll(
    dto: UserClassBulkEnrollDTO,
    service: UserClassService = Depends(get_user_class_service)
):
    """Bulk enroll users in a class"""
    return await service.bulk_enroll(dto)

@router.get("/user/{user_id}", response_model=list[UserClassViewModel])
async def get_user_enrollments(
    user_id: UUID,
    service: UserClassService = Depends(get_user_class_service)
):
    """Get all enrollments for a user"""
    return await service.get_user_enrollments(user_id)

@router.get("/user/{user_id}/summary")
async def get_enrollment_summary(
    user_id: UUID,
    service: UserClassService = Depends(get_user_class_service)
):
    """Get enrollment summary for a user"""
    return await service.get_enrollment_summary(user_id)

@router.get("/user/{user_id}/eligibility/{class_id}")
async def check_enrollment_eligibility(
    user_id: UUID,
    class_id: UUID,
    service: UserClassService = Depends(get_user_class_service)
):
    """Check if user can enroll in a class"""
    return await service.check_enrollment_eligibility(user_id, class_id)

@router.get("/class/{class_id}", response_model=list[UserClassViewModel])
async def get_class_enrollments(
    class_id: UUID,
    service: UserClassService = Depends(get_user_class_service)
):
    """Get all enrollments for a class"""
    return await service.get_class_enrollments(class_id)

@router.patch("/{enrollment_id}/deactivate")
async def unenroll_user(
    enrollment_id: UUID,
    service: UserClassService = Depends(get_user_class_service)
):
    """Unenroll a user from a class"""
    try:
        result = await service.unenroll_user(enrollment_id)
        return {"message": "User unenrolled successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))