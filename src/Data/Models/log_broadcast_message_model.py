"""Broadcast message logging model"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import LogBaseModel

class LogBroadcastMessageModel(LogBaseModel):
    __tablename__ = "log_broadcast_message"
    
    message = Column(Text, nullable=False)
    document_1_base64 = Column(Text, nullable=False)
    document_2_base64 = Column(Text, nullable=False)
    sent_whatsapp = Column(Boolean, nullable=False, default=False)
    sent_email = Column(Boolean, nullable=False, default=False)
    sent_sms = Column(Boolean, nullable=False, default=False)
    user_ip_address = Column(String(39), nullable=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)