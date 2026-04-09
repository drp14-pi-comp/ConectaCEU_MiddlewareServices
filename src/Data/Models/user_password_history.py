"""User password history model"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkBaseModel

class UserPasswordHistory(UuidPkBaseModel):
    __tablename__ = "user_password_history"
    
    password = Column(String(512), nullable=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)