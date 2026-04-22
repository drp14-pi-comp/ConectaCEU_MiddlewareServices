"""Report service - generate reports from data"""
from typing import List, Dict, Any, Optional
from uuid import UUID

from src.data.repositories.log_student_enrollment_repository import LogStudentEnrollmentRepository
from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.user_class_repository import UserClassRepository

class ReportService:
    """Service for generating reports"""
    
    def __init__(
        self,
        enrollment_log_repo: LogStudentEnrollmentRepository,
        course_repo: CourseRepository,
        user_class_repo: UserClassRepository
    ):
        self.enrollment_log_repo = enrollment_log_repo
        self.course_repo = course_repo
        self.user_class_repo = user_class_repo
    
    async def get_students_by_course(self, course_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get students enrolled by course"""
        report_data = []
        
        if course_id:
            courses = [await self.course_repo.get_by_id(course_id)]
        else:
            courses = await self.course_repo.get_all()
        
        for course in courses:
            if course:
                enrollments = await self.user_class_repo.get_active_by_class_id(UUID(bytes=course.id))
                stats = await self.enrollment_log_repo.get_enrollment_stats(UUID(bytes=course.id))
                
                report_data.append({
                    'course_id': str(UUID(bytes=course.id)),
                    'course_name': course.name,
                    'total_enrollments': len(enrollments),
                    'enrollment_stats': stats
                })
        
        return report_data
    
    async def get_course_vacancies(self) -> List[Dict[str, Any]]:
        """Get vacancies by course"""
        report_data = []
        courses = await self.course_repo.get_all()
        
        for course in courses:
            # Calculate total enrolled across all components
            total_enrolled = 0
            # This would require component and class repositories
            
            report_data.append({
                'course_id': str(UUID(bytes=course.id)),
                'course_name': course.name,
                'total_seats': course.total_seat_limit,
                'enrolled': total_enrolled,
                'available_seats': course.total_seat_limit - total_enrolled,
                'occupancy_rate': (total_enrolled / course.total_seat_limit * 100) if course.total_seat_limit > 0 else 0
            })
        
        return report_data