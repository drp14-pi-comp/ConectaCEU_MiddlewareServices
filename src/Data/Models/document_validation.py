"""Document validation model"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class DocumentValidation(UuidPkUpdatableBaseModel):
    __tablename__ = "document_validation"
    
    rejection_reason = Column(String(500), nullable=True)
    
    # Foreign keys
    document_validation_status_type_id = Column(BINARY(16), ForeignKey('document_validation_status_type.id'), nullable=False)
    document_id = Column(BINARY(16), ForeignKey('document.id'), nullable=False)