"""Enrollment waiting list model"""
from sqlalchemy import Column, ForeignKey, DateTime, Integer, func
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import Base
import uuid

class EnrollmentWaitingListModel(Base):
    __tablename__ = "enrollment_waiting_list"
    
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    course_id = Column(BINARY(16), ForeignKey('course.id'), nullable=False)
    position = Column(Integer, nullable=False)  # Queue position