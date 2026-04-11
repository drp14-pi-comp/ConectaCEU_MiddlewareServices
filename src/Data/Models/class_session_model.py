"""Class session model (individual class meetings)"""
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class ClassSessionModel(UuidPkUpdatableBaseModel):
    __tablename__ = "class_session"
    
    date = Column(DateTime, nullable=False)
    
    # Foreign keys
    class_id = Column(BINARY(16), ForeignKey('class.id'), nullable=False)