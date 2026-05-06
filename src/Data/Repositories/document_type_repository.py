"""Document type repository"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.data.models.document_type_model import DocumentTypeModel
from src.data.repositories.base.base_repository import BaseRepository

class DocumentTypeRepository(BaseRepository):
    """Repository for Document Type reference entity"""
    
    def __init__(self, session: Session):
        super().__init__(session, DocumentTypeModel)
    
    async def get_by_description(self, description: str) -> Optional[DocumentTypeModel]:
        """Get document type by description"""
        stmt = select(DocumentTypeModel).where(DocumentTypeModel.description == description)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()