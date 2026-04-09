"""User activation logging model"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import LogBaseModel

class LogUserActivation(LogBaseModel):
    __tablename__ = "log_user_activation"
    
    deactivation_reason = Column(String(500), nullable=True)
    activated = Column(Boolean, nullable=False)
    performed_by_user_ip_address = Column(String(39), nullable=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    performed_by_user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)