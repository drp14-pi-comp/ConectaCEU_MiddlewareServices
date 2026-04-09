"""Document request logging model"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import LogBaseModel

class LogDocumentRequest(LogBaseModel):
    __tablename__ = "log_document_request"
    
    user_ip_address = Column(String(39), nullable=False)
    
    # Foreign keys
    document_type_id = Column(BINARY(16), ForeignKey('document_type.id'), nullable=False)
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)