"""Report service - generate reports from data"""
from typing import List, Dict, Any, Optional
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.log_report_request_repository import LogReportRequestRepository
from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.user_course_repository import UserCourseRepository
from src.data.repositories.user_repository import UserRepository

class ReportService:
    """Service for generating reports"""
    
    def __init__(
        self,
        course_repo: CourseRepository,
        component_repo: CourseComponentRepository,
        user_course_repo: UserCourseRepository,
        user_repo: UserRepository,
        class_repo: ClassRepository,
        log_report_repo: LogReportRequestRepository
    ):
        self.course_repo = course_repo
        self.component_repo = component_repo
        self.user_course_repo = user_course_repo
        self.user_repo = user_repo
        self.class_repo = class_repo
        self.log_report_repo = log_report_repo
    
    async def get_students_by_course(
        self,
        course_id: Optional[UUID] = None,
        component_id: Optional[UUID] = None,
        requested_by_user_id: Optional[UUID] = None,
        user_ip_address: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get students enrolled by course and/or component.
        """
        try:
            if requested_by_user_id:
                await self.log_report_repo.log(
                    report_type_id=1,
                    user_id=requested_by_user_id.bytes,
                    user_ip_address=user_ip_address or "unknown"
                )

            report_data = []
            
            if course_id:
                courses = [await self.course_repo.get_by_id(course_id)]
            else:
                courses = await self.course_repo.get_all()
            
            for course in courses:
                if not course:
                    continue
                
                course_uuid = UUID(bytes=course.id)
                enrollments = await self.user_course_repo.get_active_by_course_id(course_uuid)
                
                # Get all components for this course
                if component_id:
                    components = [await self.component_repo.get_by_id(component_id)]
                else:
                    components = await self.component_repo.get_by_course_id(course_uuid)
                
                for enrollment in enrollments:
                    user_uuid = UUID(bytes=enrollment.user_id)
                    user = await self.user_repo.get_by_id(user_uuid)
                    
                    if not user:
                        continue
                    
                    # For each component, get the classes and check attendance
                    for component in components:
                        if not component:
                            continue
                        
                        component_uuid = UUID(bytes=component.id)
                        classes = await self.class_repo.get_by_component_id(component_uuid)
                        
                        for class_ in classes:
                            class_uuid = UUID(bytes=class_.id)
                            
                            report_data.append({
                                'course_id': str(course_uuid),
                                'course_name': course.name,
                                'component_id': str(component_uuid),
                                'component_name': component.name,
                                'class_id': str(class_uuid),
                                'shift_type_id': class_.shift_type_id,
                                'student_name': user.name,
                                'student_document': user.document,
                                'student_email': user.email,
                                'student_phone': user.cellphone_number,
                                'student_type_id': user.user_type_id
                            })

            return report_data
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_course_vacancies(
        self,
        course_id: Optional[UUID] = None,
        requested_by_user_id: Optional[UUID] = None,
        user_ip_address: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get vacancies by course"""
        try:
            if requested_by_user_id:
                await self.log_report_repo.log(
                    report_type_id=2,
                    user_id=requested_by_user_id.bytes,
                    user_ip_address=user_ip_address or "unknown"
                )
                
            report_data = []
            
            if course_id:
                courses = [await self.course_repo.get_by_id(course_id)]
            else:
                courses = await self.course_repo.get_all()
            
            for course in courses:
                if not course:
                    continue
                
                course_uuid = UUID(bytes=course.id)
                
                # Count enrollments directly by course
                enrollments = await self.user_course_repo.get_active_by_course_id(course_uuid)
                total_enrolled = len(enrollments)
                
                report_data.append({
                    'course_id': str(course_uuid),
                    'course_name': course.name,
                    'total_seats': course.total_seat_limit,
                    'enrolled': total_enrolled,
                    'available_seats': course.total_seat_limit - total_enrolled,
                    'occupancy_rate': round(
                        (total_enrolled / course.total_seat_limit * 100) if course.total_seat_limit > 0 else 0,
                        2
                    )
                })

            return report_data
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)