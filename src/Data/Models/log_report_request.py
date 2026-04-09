"""Report request logging model"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import LogBaseModel

class LogReportRequest(LogBaseModel):
    __tablename__ = "log_report_request"
    
    report_type_id = Column(BINARY(16), ForeignKey('report_type.id'), nullable=False)
    user_ip_address = Column(String(39), nullable=False)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)