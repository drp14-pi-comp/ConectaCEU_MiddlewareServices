"""Student enrollment log repository - Insert only"""
from sqlalchemy.orm import Session
from src.data.models.log_student_enrollment_model import LogStudentEnrollment as LogStudentEnrollmentModel
from src.data.repositories.base.base_repository import BaseRepository

class LogStudentEnrollmentRepository(BaseRepository):
    """Repository for Student Enrollment logs - Insert only"""
    
    def __init__(self, session: Session):
        super().__init__(session, LogStudentEnrollmentModel)
    
    async def log(
        self,
        enrolled: bool,
        user_id: bytes,
        user_ip_address: str,
        course_id: bytes
    ) -> LogStudentEnrollmentModel:
        """Log a student enrollment/unenrollment"""
        log = LogStudentEnrollmentModel(
            enrolled=enrolled,
            user_id=user_id,
            user_ip_address=user_ip_address,
            course_id=course_id
        )
        return await self.create(log)