"""Course creation log repository - Insert only"""
from sqlalchemy.orm import Session
from src.data.models.log_course_creation_model import LogCourseCreation as LogCourseCreationModel
from src.data.repositories.base.base_repository import BaseRepository

class LogCourseCreationRepository(BaseRepository):
    """Repository for Course Creation logs - Insert only"""
    
    def __init__(self, session: Session):
        super().__init__(session, LogCourseCreationModel)
    
    async def log(
        self,
        user_id: bytes,
        user_ip_address: str,
        course_id: bytes
    ) -> LogCourseCreationModel:
        """Log a course creation"""
        log = LogCourseCreationModel(
            user_id=user_id,
            user_ip_address=user_ip_address,
            course_id=course_id
        )
        return await self.create(log)