"""Course creation logging model"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import LogBaseModel

class LogCourseCreation(LogBaseModel):
    __tablename__ = "log_course_creation"
    
    user_ip_address = Column(String(39), nullable=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    course_id = Column(BINARY(16), ForeignKey('course.id'), nullable=False)