"""User class enrollment model"""
from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class UserClass(UuidPkUpdatableBaseModel):
    __tablename__ = "user_class"
    
    active = Column(Boolean, nullable=False, default=True)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    class_id = Column(BINARY(16), ForeignKey('class.id'), nullable=False)