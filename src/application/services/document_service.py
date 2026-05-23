"""Document service - business logic for Document entity"""
from typing import List, Optional
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.models.document_model import DocumentModel
from src.data.models.user_model import UserModel
from src.data.repositories.address_repository import AddressRepository
from src.data.repositories.document_repository import DocumentRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.data.repositories.user_repository import UserRepository
from src.domain.constants.document_types import DocumentTypes
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.view_models.document_view_model import DocumentViewModel
from src.infrastructure.handlers.datetime_handler import DateTimeHandler
from src.infrastructure.handlers.format_handler import FormatHandler

class DocumentService(BaseService):
    """Service for Document business logic"""
    
    def __init__(
        self,
        repository: DocumentRepository,
        user_repo: UserRepository,
        address_repo: AddressRepository
    ):
        super().__init__(repository, 'document', mapper_class=ModelToEntityMapper)
        self.repository = repository
        self.user_repo = user_repo
        self.address_repo = address_repo
    
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
            student_photo_doc_type_id = 4
            is_user_photo = model.document_type_id == student_photo_doc_type_id;
            existing_document = await self.repository.get_latest_document(model)

            if existing_document:
                existing_document.base64 = dto.base64
                self.repository.update(existing_document)

                if is_user_photo:
                    existing_student_card = (await self.repository.get_by_type(
                        UUID(bytes=user.id),
                        student_photo_doc_type_id
                    ))[0]
                    existing_student_card.base64 = await self._get_student_card_base64(user, dto.base64)
                    await self.repository.update(existing_student_card)
            else:
                saved_model = await self.repository.create(model)

                if is_user_photo:
                    self._create_student_card(user, dto.base64)

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
        logged_user_id: Optional[UUID] = None,
        user_ip_address: Optional[str] = None
    ) -> List[DocumentViewModel]:
        """Get a document by type"""
        try:
            documents = await self.repository.get_by_type(user_id, document_type_id)
            if not documents or len(documents) <= 0:
                raise ValueError("Nenhum documento encontrado")
            
            if logged_user_id and user_ip_address:
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

    async def get_management_document_template(self, document_type_id: int) -> Optional[dict]:
        try:
            if not DocumentTypes.is_template_type(document_type_id):
                raise ValueError('Tipo de documento inválido')
            
            document_base64: str = ''

            match DocumentTypes(document_type_id):
                case DocumentTypes.HEALTH_CERTIFICATE_TEMPLATE:
                    document_base64 = self._get_health_certificate_template()
                case DocumentTypes.REGISTER_USER_FORM_TEMPLATE:
                    document_base64 = self._get_register_user_form_template()
                case DocumentTypes.ATTENDANCE_LIST_TEMPLATE:
                    document_base64 = await self._get_attendance_list_template()
                case _:
                    return None

            return { 'base64': document_base64 }
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

    # PDF rendering
    def _render_to_base64(self, html: str) -> str:
        """Render the HTML as PDF"""
        from src.infrastructure.pdf.pdf_render_service import PdfRenderService

        return PdfRenderService.render_to_base64(html)

    # Student card
    async def _get_student_card_base64(self, user: UserModel, photo_base_64: str) -> str:
        if len(photo_base_64) <= 0:
            raise ValueError('Foto de usuário não pode ser vazia')
        
        card_html = ''
        with open("src/templates/docs/student_card.html", "r", encoding="utf-8") as f:
            card_html = f.read()
        card_html = card_html.replace('${studentSequential}', str(user.student_sequential))
        card_html = card_html.replace('${name}', user.name)
        card_html = card_html.replace('${document}', user.document)
        card_html = card_html.replace('${birthdate}', user.birthdate.strftime("%d/%m/%Y"))
        card_html = card_html.replace('${studentPhotoBase64}', photo_base_64.base64)
        user_address = (await self.address_repo.get_by_user_id(UUID(bytes=user.id)))[0]
        card_html = card_html.replace(
            '${userFullAddress}',
            f'{user_address.street}, {user_address.number} - {user_address.neighborhood}, {FormatHandler.format_zip_code(user_address.zip_code)}' if user_address else ''
        )
        student_phone_number = user.cellphone_number if user.cellphone_number else ''
        card_html = card_html.replace('${userPhoneNumber}', FormatHandler.format_phone(student_phone_number))

        return self._render_to_base64(card_html)
    
    async def _create_student_card(self, user: UserModel, photo_base_64: str) -> DocumentCreateDTO:
        user_id: UUID = UUID(bytes=user.id)
        card = DocumentModel(
            base64=self._get_student_card_base64(user, photo_base_64),
            user_id=str(user_id),
            document_type_id=8,
            is_front=None,
            legal_representative_id=None
        )
        
        doc_entity = DtoToEntityMapper.document(card)
        doc_entity.user_id = user_id
        doc_model = EntityToModelMapper.document(doc_entity)

        await self.repository.create(doc_model)
    
    # Health certificate
    def _get_health_certificate_template(self) -> str:
        """Get the health certificate template"""
        with open('src/templates/docs/health_certificate.html', 'r', encoding='utf-8') as f:
            return self._render_to_base64(f.read())

    # Register user form template
    def _get_register_user_form_template(self) -> str:
        "Get the register user form template"
        html = ''
        with open('src/templates/docs/register_user_form_template.html', 'r', encoding='utf-8') as f:
            # return f.read()
            html = f.read()
        
        from src.infrastructure.pdf.pdf_render_service import PdfRenderService

        # testing
        pdf_bytes = PdfRenderService.render_to_bytes(html)
        with open("test.pdf", "wb") as f:
            f.write(pdf_bytes)
    
    # Attendance list template
    async def _get_attendance_list_template(self) -> str:
        """Get the attendance list template"""
        html = ''
        with open('src/templates/docs/attendance_list_template.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        return html