"""Report service - generate reports from data"""
from typing import List, Dict, Any, Optional
from uuid import UUID

from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
from src.data.repositories.log_student_enrollment_repository import LogStudentEnrollmentRepository
from src.data.repositories.course_repository import CourseRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.user_repository import UserRepository

class ReportService:
    """Service for generating reports"""
    
    def __init__(
        self,
        course_repo: CourseRepository,
        component_repo: CourseComponentRepository,
        user_class_repo: UserClassRepository,
        user_repo: UserRepository,
        class_repo: ClassRepository
    ):
        self.course_repo = course_repo
        self.component_repo = component_repo
        self.user_class_repo = user_class_repo
        self.user_repo = user_repo
        self.class_repo = class_repo
    
    async def get_students_by_course(
        self,
        course_id: Optional[UUID] = None,
        component_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get students enrolled by course and/or component.
        
        Args:
            course_id: Optional filter by course
            component_id: Optional filter by component
            
        Returns:
            List with each item containing course, component, and student details
        """
        report_data = []
        
        # Get courses (all or specific)
        if course_id:
            courses = [await self.course_repo.get_by_id(course_id)]
        else:
            courses = await self.course_repo.get_all()
        
        for course in courses:
            if not course:
                continue
            
            course_uuid = UUID(bytes=course.id)
            
            # Get components for this course (all or specific)
            if component_id:
                components = [await self.component_repo.get_by_id(component_id)]
            else:
                components = await self.component_repo.get_by_course_id(course_uuid)
            
            for component in components:
                if not component:
                    continue
                
                component_uuid = UUID(bytes=component.id)
                
                # Get classes for this component
                classes = await self.class_repo.get_by_component_id(component_uuid)
                
                for class_ in classes:
                    class_uuid = UUID(bytes=class_.id)
                    
                    # Get active enrollments for this class
                    enrollments = await self.user_class_repo.get_active_by_class_id(class_uuid)
                    
                    for enrollment in enrollments:
                        user_uuid = UUID(bytes=enrollment.user_id)
                        user = await self.user_repo.get_by_id(user_uuid)
                        
                        if user:
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