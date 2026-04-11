"""Class attendance model"""
from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class ClassAttendanceModel(UuidPkUpdatableBaseModel):
    __tablename__ = "attendance"
    
    attended = Column(Boolean, nullable=False, default=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    class_session_id = Column(BINARY(16), ForeignKey('class_session.id'), nullable=False)