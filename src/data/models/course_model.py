"""Course model"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class CourseModel(UuidPkUpdatableBaseModel):
    __tablename__ = "course"
    
    name = Column(String(100), unique=True, nullable=False)
    total_seat_limit = Column(Integer, nullable=False)
    workload = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    
    # Foreign keys
    responsible_educator_1 = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    responsible_educator_2 = Column(BINARY(16), ForeignKey('user.id'), nullable=True)
    shift_type_id = Column(Integer, ForeignKey('shift_type.id'), nullable=False)