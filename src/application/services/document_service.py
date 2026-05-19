"""Document service - business logic for Document entity"""
from typing import List
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.models.document_model import DocumentModel
from src.data.repositories.document_repository import DocumentRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.data.repositories.user_repository import UserRepository
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.view_models.document_view_model import DocumentViewModel
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class DocumentService(BaseService):
    """Service for Document business logic"""
    
    def __init__(
        self,
        repository: DocumentRepository,
        user_repo: UserRepository
    ):
        super().__init__(repository, 'document', mapper_class=ModelToEntityMapper)
        self.repository = repository
        self.user_repo = user_repo
    
    async def upload_document(self, dto: DocumentCreateDTO) -> DocumentViewModel:
        """Upload a new document"""
        try:
            if len(dto.base64) <= 0:
                raise ValueError('Conteúdo do documento não pode ser vazio')
            if not dto.user_id:
                raise ValueError('Documento precisa estar atrelado a um usuário')
            user = await self.user_repo.get_by_id(UUID(dto.user_id))
            if not user:
                raise ValueError('Usuário não encontrado')
            entity = DtoToEntityMapper.document(dto)
            model = EntityToModelMapper.document(entity)
            existing_document = await self.repository.get_latest_document(model)
            if existing_document:
                existing_document.base64 = dto.base64
                self.repository.update(existing_document)
            else:
                saved_model = await self.repository.create(model)
            self._create_pending_validation(model)
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
    
    async def get_document_by_id(
        self, 
        document_id: UUID,
        user_id: UUID,
        user_ip_address: str
    ) -> dict:
        """Get document and log the request"""
        try:
            document: DocumentModel = await self.repository.get_by_id(document_id)
            if not document:
                raise ValueError("Nenhum documento encontrado")
            
            # Log document request
            from src.data.repositories.log_document_request_repository import LogDocumentRequestRepository
            log_repo = LogDocumentRequestRepository(self.repository.session)
            await log_repo.log(
                document_id=document.id,
                user_id=user_id.bytes,
                user_ip_address=user_ip_address
            )

            self.repository.session.commit()
            
            entity = ModelToEntityMapper.document(document)

            return EntityToViewModelMapper.document(entity).model_dump()
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
        
    async def get_documents_by_type(
        self,
        user_id: UUID,
        document_type_id: int,
        logged_user_id: UUID,
        user_ip_address: str
    ) -> List[DocumentViewModel]:
        """Get a document by type"""
        try:
            documents = await self.repository.get_by_type(user_id, document_type_id)
            if not documents or len(documents) <= 0:
                raise ValueError("Nenhum documento encontrado")
            
            for document in documents:
                # Log document request
                from src.data.repositories.log_document_request_repository import LogDocumentRequestRepository
                log_repo = LogDocumentRequestRepository(self.repository.session)
                await log_repo.log(
                    document_id=document.id,
                    user_id=logged_user_id.bytes,
                    user_ip_address=user_ip_address
                )

            self.repository.session.commit()
            
            entities = [ModelToEntityMapper.document(model) for model in documents]

            return [EntityToViewModelMapper.document(entity) for entity in entities]
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document"""
        try:
            document = await self.repository.get_by_id(document_id)
            if not document:
                raise ValueError("Nenhum documento encontrado")
            
            result = await self.repository.delete(document_id)
            self.repository.session.commit()

            return result
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)

    async def _create_pending_validation(self, document: DocumentModel) -> None:
        """Create pending validation for secretary review"""
        from uuid import uuid4
        from src.domain.entities.document_validation import DocumentValidation
        from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
        from src.data.repositories.document_validation_repository import DocumentValidationRepository
        doc_validation_repo = DocumentValidationRepository(self.repository.session)
        
        validation = DocumentValidation(
            id=uuid4(),
            created_at=DateTimeHandler.now(),
            updated_at=None,
            rejection_reason=None,
            document_validation_status_type_id=1,  # Pending
            document_id=UUID(bytes=document.id)
        )
        validation_model = EntityToModelMapper.document_validation(validation)
        await doc_validation_repo.create(validation_model)