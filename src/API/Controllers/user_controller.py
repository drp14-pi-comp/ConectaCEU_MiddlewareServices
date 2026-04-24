"""User controller"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.application.services.user_service import UserService
from src.application.services.user_password_history_service import UserPasswordHistoryService
from src.data.repositories.user_repository import UserRepository
from src.data.repositories.user_password_history_repository import UserPasswordHistoryRepository
from src.data.db_context.database import get_db
from src.domain.dtos.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserFilterDTO,
    PasswordChangeDTO
)
from src.domain.view_models.user_view_model import UserViewModel

router = APIRouter(prefix="/user", tags=["User"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    user_repo = UserRepository(db)
    password_history_repo = UserPasswordHistoryRepository(db)
    password_history_service = UserPasswordHistoryService(password_history_repo)
    return UserService(user_repo, password_history_service)


@router.post("/", response_model=UserViewModel, status_code=status.HTTP_201_CREATED)
async def create_user(
    dto: UserCreateDTO,
    service: UserService = Depends(get_user_service)
):
    """Create a new user"""
    try:
        return await service.create_user(dto)
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
    service: UserService = Depends(get_user_service)
):
    """List users with filters and pagination"""
    return await service.find_users(
        name=name,
        document=document,
        email=email,
        phoneNumber=phoneNumber,
        user_type_id=user_type_id,
        active=active,
        page=page,
        page_size=page_size
    )


@router.get("/educators", response_model=dict)
async def get_educators(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    """Get all educators"""
    return await service.get_educators(page, page_size)


@router.get("/students", response_model=dict)
async def get_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    """Get all students"""
    return await service.get_students(page, page_size)


@router.get("/{user_id}", response_model=UserViewModel)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserViewModel)
async def update_user(
    user_id: UUID,
    dto: UserUpdateDTO,
    service: UserService = Depends(get_user_service)
):
    """Update user information"""
    try:
        user = await service.update_user(user_id, dto)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    reason: Optional[str] = None,
    service: UserService = Depends(get_user_service)
):
    """Deactivate a user account"""
    try:
        result = await service.deactivate_user(user_id, reason)
        return {"message": "User deactivated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    """Activate a user account"""
    try:
        result = await service.activate_user(user_id)
        return {"message": "User activated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/password")
async def change_password(
    user_id: UUID,
    dto: PasswordChangeDTO,
    service: UserService = Depends(get_user_service)
):
    """Change user password"""
    try:
        result = await service.change_password(user_id, dto)
        return {"message": "Password changed successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/document/{document}", response_model=UserViewModel)
async def get_user_by_document(
    document: str,
    service: UserService = Depends(get_user_service)
):
    """Get user by document (CPF)"""
    user = await service.repository.get_by_document(document)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
    from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
    
    entity = ModelToEntityMapper.user(user)
    return EntityToViewModelMapper.user(entity)


@router.get("/email/{email}", response_model=UserViewModel)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service)
):
    """Get user by email"""
    user = await service.repository.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
    from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
    
    entity = ModelToEntityMapper.user(user)
    return EntityToViewModelMapper.user(entity)