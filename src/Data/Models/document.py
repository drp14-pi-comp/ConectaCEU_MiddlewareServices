"""Document model"""
from sqlalchemy import Column, Boolean, ForeignKey, Text
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkUpdatableBaseModel

class Document(UuidPkUpdatableBaseModel):
    __tablename__ = "document"
    
    base64 = Column(Text, nullable=False)
    is_front = Column(Boolean, nullable=True)
    
    # Foreign keys
    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)
    document_type_id = Column(BINARY(16), ForeignKey('document_type.id'), nullable=False)
    legal_representative_id = Column(BINARY(16), ForeignKey('legal_representative.id'), nullable=True)