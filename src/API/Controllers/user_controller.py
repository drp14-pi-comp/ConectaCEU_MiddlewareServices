"""User controller"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session

from src.application.services.user_service import UserService
from src.application.services.user_password_history_service import UserPasswordHistoryService
from src.data.repositories.address_repository import AddressRepository
from src.data.repositories.document_repository import DocumentRepository
from src.data.repositories.document_validation_repository import DocumentValidationRepository
from src.data.repositories.legal_representative_repository import LegalRepresentativeRepository
from src.data.repositories.profiles_to_exclude_repository import ProfilesToExcludeRepository
from src.data.repositories.user_repository import UserRepository
from src.data.repositories.user_password_history_repository import UserPasswordHistoryRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.dtos.user_dto import UserCreateDTO, UserUpdateDTO, PasswordChangeDTO
from src.domain.view_models.user_view_model import UserViewModel
from src.domain.entities.user import User

router = APIRouter(
    prefix="/user",
    tags=["User"],
    dependencies=[Depends(get_current_active_user)]
)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    user_repo = UserRepository(db)
    password_history_repo = UserPasswordHistoryRepository(db)
    password_history_service = UserPasswordHistoryService(password_history_repo)
    document_repo = DocumentRepository(db)
    address_repo = AddressRepository(db)
    legal_rep_repo = LegalRepresentativeRepository(db)
    doc_validation_repo = DocumentValidationRepository(db)
    profiles_to_exclude_repo = ProfilesToExcludeRepository(db)
    return UserService(
        user_repo,
        password_history_service,
        document_repo,
        address_repo,
        legal_rep_repo,
        doc_validation_repo,
        profiles_to_exclude_repo
    )


@router.post("/", response_model=UserViewModel, status_code=status.HTTP_201_CREATED)
async def create_user(
    dto: UserCreateDTO,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    Create a new user (Admin/Secretary only).
    Documents are auto-approved.
    """
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can create users")
    
    try:
        return await service.create_user(dto, created_by_user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    request: Request,
    user_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    Deactivate a user account. Admin (1) and Secretary (2) only.
    """
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can deactivate users")
    
    try:
        user_ip = request.client.host if request.client else "unknown"
        result = await service.deactivate_user(
            user_id,
            reason=reason,
            performed_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
        return {"message": "User deactivated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/activate")
async def activate_user(
    request: Request,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    Activate a user account. Admin (1) and Secretary (2) only.
    """
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can activate users")
    
    try:
        user_ip = request.client.host if request.client else "unknown"
        result = await service.activate_user(
            user_id,
            performed_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
        return {"message": "User activated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=dict)
async def list_users(
    name: Optional[str] = Query(None),
    document: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phoneNumber: Optional[str] = Query(None),
    user_type_id: Optional[int] = Query(None),
    active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    List users with filters and pagination.
    - Admin/Secretary: can list all
    - Coordinator/Educator: can list students only
    """
    # Admins and Secretaries can list all users
    if current_user.user_type_id in [1, 2]:
        return await service.find_users(
            name=name, document=document, email=email,
            phoneNumber=phoneNumber, user_type_id=user_type_id,
            active=active, page=page, page_size=page_size
        )
    
    # Coordinators and Educators can only list students
    if current_user.user_type_id in [3, 4]:
        return await service.find_users(
            name=name,
            document=document,
            email=email,
            phoneNumber=phoneNumber,
            user_type_id=5,  # Students only
            active=active,
            page=page,
            page_size=page_size
        )
    
    raise HTTPException(status_code=403, detail="Cannot list users")


@router.get("/students", response_model=dict)
async def list_students(
    name: Optional[str] = Query(None),
    document: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phoneNumber: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    List students with all related data.
    - Admin/Secretary/Coordinator/Educator: can list
    """
    if current_user.user_type_id not in [1, 2, 3, 4]:
        raise HTTPException(status_code=403, detail="Only staff can list students")
    
    return await service.find_students(
        name=name,
        document=document,
        email=email,
        phoneNumber=phoneNumber,
        active=active,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserViewModel)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get user by ID.
    - Staff can view any user
    - Users can view themselves
    """
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.user_type_id not in [1, 2] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own profile")
    
    return user


@router.put("/{user_id}", response_model=UserViewModel)
async def update_user(
    user_id: UUID,
    dto: UserUpdateDTO,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    Update user information.
    - Admin/Secretary can update any user
    - Users can update themselves
    """
    if current_user.user_type_id not in [1, 2] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only update your own profile")
    
    try:
        user = await service.update_user(user_id, dto)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/password")
async def change_password(
    user_id: UUID,
    dto: PasswordChangeDTO,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """
    Change user password.
    - Users can only change their own password
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only change your own password")
    
    try:
        result = await service.change_password(user_id, dto)
        return {"message": "Password changed successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))