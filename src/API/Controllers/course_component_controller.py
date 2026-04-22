"""Course component controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.course_component_service import CourseComponentService
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.db_context.database import get_db
from src.domain.dtos.course_component_dto import CourseComponentCreateDTO, CourseComponentUpdateDTO
from src.domain.view_models.course_component_view_model import CourseComponentViewModel

router = APIRouter(prefix="/component", tags=["Course Component"])

def get_component_service(db: Session = Depends(get_db)) -> CourseComponentService:
    repository = CourseComponentRepository(db)
    return CourseComponentService(repository)

@router.post("/", response_model=CourseComponentViewModel, status_code=status.HTTP_201_CREATED)
async def create_component(
    dto: CourseComponentCreateDTO,
    service: CourseComponentService = Depends(get_component_service)
):
    """Create a new course component"""
    try:
        return await service.create_component(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/course/{course_id}", response_model=list[CourseComponentViewModel])
async def get_course_components(
    course_id: UUID,
    service: CourseComponentService = Depends(get_component_service)
):
    """Get all components for a course"""
    return await service.get_course_components(course_id)

@router.get("/{component_id}", response_model=CourseComponentViewModel)
async def get_component(
    component_id: UUID,
    service: CourseComponentService = Depends(get_component_service)
):
    """Get component by ID"""
    component = await service.get_by_id(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component

@router.put("/{component_id}", response_model=CourseComponentViewModel)
async def update_component(
    component_id: UUID,
    dto: CourseComponentUpdateDTO,
    service: CourseComponentService = Depends(get_component_service)
):
    """Update a component"""
    try:
        component = await service.update_component(component_id, dto)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        return component
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{component_id}/deactivate")
async def deactivate_component(
    component_id: UUID,
    service: CourseComponentService = Depends(get_component_service)
):
    """Deactivate a component"""
    try:
        result = await service.deactivate_component(component_id)
        return {"message": "Component deactivated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))