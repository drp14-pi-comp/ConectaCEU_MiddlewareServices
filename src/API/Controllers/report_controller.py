"""Report controller"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.application.services.report_service import ReportService
from src.data.repositories.log_student_enrollment_repository import LogStudentEnrollmentRepository
from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.db_context.database import get_db
from src.domain.dtos.report_request_dto import ReportRequestDTO

router = APIRouter(prefix="/report", tags=["Report"])

def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    enrollment_log_repo = LogStudentEnrollmentRepository(db)
    course_repo = CourseRepository(db)
    user_class_repo = UserClassRepository(db)
    return ReportService(enrollment_log_repo, course_repo, user_class_repo)

@router.get("/students-by-course")
async def get_students_by_course(
    course_id: Optional[UUID] = None,
    service: ReportService = Depends(get_report_service)
):
    """Get students enrolled by course"""
    try:
        return await service.get_students_by_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/course-vacancies")
async def get_course_vacancies(
    service: ReportService = Depends(get_report_service)
):
    """Get vacancies by course"""
    try:
        return await service.get_course_vacancies()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))