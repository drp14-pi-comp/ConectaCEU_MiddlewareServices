"""User class enrollment controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.user_class_service import UserClassService
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.class_session_repository import ClassSessionRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.dtos.user_class_dto import UserClassEnrollDTO, UserClassBulkEnrollDTO
from src.domain.view_models.user_class_view_model import UserClassViewModel
from src.domain.entities.user import User

router = APIRouter(
    prefix="/enrollment",
    tags=["Enrollment"],
    dependencies=[Depends(get_current_active_user)]
)


def get_user_class_service(db: Session = Depends(get_db)) -> UserClassService:
    """Dependency injection for UserClassService"""
    repository = UserClassRepository(db)
    class_repo = ClassRepository(db)
    session_repo = ClassSessionRepository(db)
    component_repo = CourseComponentRepository(db)
    return UserClassService(repository, class_repo, session_repo, component_repo)


@router.post("/", response_model=UserClassViewModel, status_code=status.HTTP_201_CREATED)
async def enroll_user(
    request: Request,
    dto: UserClassEnrollDTO,
    current_user: User = Depends(get_current_active_user),
    service: UserClassService = Depends(get_user_class_service)
):
    """Enroll a user in a class."""
    try:
        user_ip = request.client.host if request.client else "unknown"
        return await service.enroll_user(
            dto,
            enrolled_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk")
async def bulk_enroll(
    dto: UserClassBulkEnrollDTO,
    current_user: User = Depends(get_current_active_user),
    service: UserClassService = Depends(get_user_class_service)
):
    """
    Bulk enroll users in a class.
    Admin (1), Secretary (2), Coordinator (3), Educator (4) only.
    """
    if current_user.user_type_id not in [1, 2, 3, 4]:
        raise HTTPException(status_code=403, detail="Only staff can bulk enroll students")
    
    return await service.bulk_enroll(dto)


@router.get("/user/{user_id}", response_model=list[UserClassViewModel])
async def get_user_enrollments(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserClassService = Depends(get_user_class_service)
):
    """
    Get all enrollments for a user.
    - Staff can view any user
    - Users can view their own
    """
    if current_user.user_type_id not in [1, 2, 3, 4] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own enrollments")
    
    return await service.get_user_enrollments(user_id)


@router.get("/user/{user_id}/summary")
async def get_enrollment_summary(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserClassService = Depends(get_user_class_service)
):
    """
    Get enrollment summary for a user.
    - Staff can view any user
    - Users can view their own
    """
    if current_user.user_type_id not in [1, 2, 3, 4] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own summary")
    
    return await service.get_enrollment_summary(user_id)


@router.get("/class/{class_id}", response_model=list[UserClassViewModel])
async def get_class_enrollments(
    class_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserClassService = Depends(get_user_class_service)
):
    """
    Get all enrollments for a class.
    Admin (1), Secretary (2), Coordinator (3), Educator (4) only.
    """
    if current_user.user_type_id not in [1, 2, 3, 4]:
        raise HTTPException(status_code=403, detail="Only staff can view class enrollments")
    
    return await service.get_class_enrollments(class_id)


@router.patch("/{enrollment_id}/unenroll")
async def unenroll_user(
    request: Request,
    enrollment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserClassService = Depends(get_user_class_service)
):
    """Unenroll a user from a class."""
    try:
        user_ip = request.client.host if request.client else "unknown"
        result = await service.unenroll_user(
            enrollment_id,
            unenrolled_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
        return {"message": "User unenrolled successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))