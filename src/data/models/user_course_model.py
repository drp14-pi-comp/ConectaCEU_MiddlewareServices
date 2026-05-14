"""User course enrollment model"""
from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class UserCourseModel(UuidPkUpdatableBaseModel):
    __tablename__ = "user_course"
    
    active = Column(Boolean, nullable=False, default=True)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    course_id = Column(BINARY(16), ForeignKey('course.id'), nullable=False)