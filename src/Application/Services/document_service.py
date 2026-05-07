"""Document service - business logic for Document entity"""
from typing import List
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.repositories.document_repository import DocumentRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.view_models.document_view_model import DocumentViewModel

class DocumentService(BaseService):
    """Service for Document business logic"""
    
    def __init__(self, repository: DocumentRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def upload_document(self, dto: DocumentCreateDTO) -> DocumentViewModel:
        """Upload a new document"""
        try:
            entity = DtoToEntityMapper.document(dto)
            model = EntityToModelMapper.document(entity)
            saved_model = await self.repository.create(model)
            self.repository.session.commit()
            saved_entity = ModelToEntityMapper.document(saved_model)
            return EntityToViewModelMapper.document(saved_entity)
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_user_documents(self, user_id: UUID) -> List[DocumentViewModel]:
        """Get all documents for a user"""
        try:
            models = await self.repository.get_by_user_id(user_id)
            entities = [ModelToEntityMapper.document(model) for model in models]
            return [EntityToViewModelMapper.document(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def get_document_for_download(
        self, 
        document_id: UUID,
        user_id: UUID,
        user_ip_address: str
    ) -> dict:
        """Get document for download and log the request"""
        try:
            document = await self.repository.get_by_id(document_id)
            if not document:
                raise ValueError("Document not found")
            
            # Log document request
            from src.data.repositories.log_document_request_repository import LogDocumentRequestRepository
            log_repo = LogDocumentRequestRepository(self.repository.session)
            await log_repo.log(
                document_type_id=document.document_type_id,
                user_id=user_id.bytes,
                user_ip_address=user_ip_address
            )
            
            entity = ModelToEntityMapper.document(document)

            return EntityToViewModelMapper.document(entity).model_dump()
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document"""
        try:
            document = await self.repository.get_by_id(document_id)
            if not document:
                raise ValueError("Document not found")
            
            result = await self.repository.delete(document_id)
            self.repository.session.commit()

            return result
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)