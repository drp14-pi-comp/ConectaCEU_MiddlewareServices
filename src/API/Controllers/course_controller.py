"""Course controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session

from src.application.services.course_service import CourseService
from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.db_context.database import get_db
from src.domain.dtos.course_dto import CourseCreateDTO, CourseUpdateDTO, CourseFilterDTO
from src.domain.view_models.course_view_model import CourseViewModel

router = APIRouter(prefix="/course", tags=["Course"])

def get_course_service(db: Session = Depends(get_db)) -> CourseService:
    course_repo = CourseRepository(db)
    component_repo = CourseComponentRepository(db)
    class_repo = ClassRepository(db)
    user_class_repo = UserClassRepository(db)
    return CourseService(course_repo, component_repo, class_repo, user_class_repo)

@router.post("/", response_model=CourseViewModel, status_code=status.HTTP_201_CREATED)
async def create_course(
    request: Request,
    dto: CourseCreateDTO,
    created_by_user_id: str,
    service: CourseService = Depends(get_course_service)
):
    """Create a new course with components"""
    try:
        user_ip = request.client.host if request.client else "unknown"
        return await service.create_course(
            dto,
            UUID(created_by_user_id),
            user_ip_address=user_ip
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
async def list_courses(
    name: str = Query(None),
    active: bool = Query(None),
    educator_id: UUID = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: CourseService = Depends(get_course_service)
):
    """List courses with filters"""
    filters = CourseFilterDTO(
        name=name,
        active=active,
        educator_id=str(educator_id) if educator_id else None,
        page=page,
        page_size=page_size
    )
    return await service.find_courses(**filters.model_dump(exclude_none=True))

@router.get("/{course_id}", response_model=CourseViewModel)
async def get_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service)
):
    """Get course by ID"""
    course = await service.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/{course_id}/details")
async def get_course_details(
    course_id: UUID,
    service: CourseService = Depends(get_course_service)
):
    """Get course with components"""
    try:
        return await service.get_course_with_components(course_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{course_id}", response_model=CourseViewModel)
async def update_course(
    course_id: UUID,
    dto: CourseUpdateDTO,
    service: CourseService = Depends(get_course_service)
):
    """Update a course"""
    try:
        course = await service.update_course(course_id, dto)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{course_id}/deactivate")
async def deactivate_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service)
):
    """Deactivate a course"""
    try:
        result = await service.deactivate_course(course_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{course_id}/activate")
async def activate_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service)
):
    """Activate a course"""
    try:
        result = await service.activate_course(course_id)
        return {"message": "Course activated successfully", "success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))