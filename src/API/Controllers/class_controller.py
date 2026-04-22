"""Class controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.application.services.class_service import ClassService
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.db_context.database import get_db
from src.domain.dtos.class_dto import ClassCreateDTO, ClassUpdateDTO, ClassFilterDTO
from src.domain.view_models.class_view_model import ClassViewModel

router = APIRouter(prefix="/class", tags=["Class"])

def get_class_service(db: Session = Depends(get_db)) -> ClassService:
    class_repo = ClassRepository(db)
    component_repo = CourseComponentRepository(db)
    user_class_repo = UserClassRepository(db)
    return ClassService(class_repo, component_repo, user_class_repo)

@router.post("/", response_model=ClassViewModel, status_code=status.HTTP_201_CREATED)
async def create_class(
    dto: ClassCreateDTO,
    service: ClassService = Depends(get_class_service)
):
    """Create a new class"""
    try:
        return await service.create_class(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
async def list_classes(
    component_id: UUID = Query(None),
    shift_type_id: int = Query(None),
    active: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: ClassService = Depends(get_class_service)
):
    """List classes with filters"""
    filters = ClassFilterDTO(
        component_id=str(component_id) if component_id else None,
        shift_type_id=shift_type_id,
        active=active,
        page=page,
        page_size=page_size
    )
    return await service.find_classes(filters)

@router.get("/{class_id}", response_model=ClassViewModel)
async def get_class(
    class_id: UUID,
    service: ClassService = Depends(get_class_service)
):
    """Get class by ID"""
    class_ = await service.get_by_id(class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.get("/{class_id}/seats")
async def get_available_seats(
    class_id: UUID,
    service: ClassService = Depends(get_class_service)
):
    """Get available seats for a class"""
    try:
        return await service.get_available_seats(class_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{class_id}", response_model=ClassViewModel)
async def update_class(
    class_id: UUID,
    dto: ClassUpdateDTO,
    service: ClassService = Depends(get_class_service)
):
    """Update a class"""
    try:
        class_ = await service.update_class(class_id, dto)
        if not class_:
            raise HTTPException(status_code=404, detail="Class not found")
        return class_
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{class_id}/deactivate")
async def deactivate_class(
    class_id: UUID,
    service: ClassService = Depends(get_class_service)
):
    """Deactivate a class"""
    try:
        result = await service.deactivate_class(class_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{class_id}/activate")
async def activate_class(
    class_id: UUID,
    service: ClassService = Depends(get_class_service)
):
    """Activate a class"""
    try:
        result = await service.activate_class(class_id)
        return {"message": "Class activated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))