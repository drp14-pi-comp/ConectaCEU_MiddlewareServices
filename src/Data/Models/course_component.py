"""Course component model"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class CourseComponent(UuidPkUpdatableBaseModel):
    __tablename__ = "component"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), unique=True, nullable=False)
    seat_limit_per_class = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    
    # Foreign keys
    course_id = Column(BINARY(16), ForeignKey('course.id'), nullable=False)