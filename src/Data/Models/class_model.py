"""Class model"""
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class ClassModel(UuidPkUpdatableBaseModel):
    __tablename__ = "class"
    
    seats_in_use = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)
    
    # Foreign keys
    component_id = Column(BINARY(16), ForeignKey('course_component.id'), nullable=False)
    shift_type_id = Column(BINARY(16), ForeignKey('shift_type.id'), nullable=False)