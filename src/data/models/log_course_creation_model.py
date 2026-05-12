"""Course creation logging model"""
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import LogBaseModel

class LogCourseCreationModel(LogBaseModel):
    __tablename__ = "log_course_creation"
    
    name = Column(String(100), nullable=False)
    total_seat_limit = Column(Integer, nullable=False)
    workload = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    user_ip_address = Column(String(39), nullable=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)