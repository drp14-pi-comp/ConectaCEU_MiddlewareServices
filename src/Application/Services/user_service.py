"""User service - business logic for User entity"""
from typing import Optional
from uuid import UUID
import bcrypt

from src.application.services.user_password_history_service import UserPasswordHistoryService
from src.data.repositories.address_repository import AddressRepository
from src.data.repositories.document_repository import DocumentRepository
from src.data.repositories.legal_representative_repository import LegalRepresentativeRepository
from src.data.repositories.user_repository import UserRepository
from src.data.repositories.user_password_history_repository import UserPasswordHistoryRepository
from src.application.services.base_service import BaseService
from src.application.mappers.dto_to_entity_mapper import DtoToEntityMapper
from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.application.mappers.update_mapper import UpdateMapper
from src.domain.dtos.user_dto import UserCreateDTO, UserUpdateDTO, UserLoginDTO, PasswordChangeDTO
from src.domain.view_models.user_view_model import UserViewModel
from src.domain.entities.user import User
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class UserService(BaseService):
    """Service for User business logic"""
    
    def __init__(
        self,
        repository: UserRepository,
        password_history_service: UserPasswordHistoryService,
        document_repo: DocumentRepository,
        address_repo: AddressRepository,
        legal_rep_repo: LegalRepresentativeRepository
    ):
        super().__init__(repository)
        self.repository = repository
        self.password_history_service = password_history_service
        self.document_repo = document_repo
        self.address_repo = address_repo
        self.legal_rep_repo = legal_rep_repo
    
    async def create_user(self, dto: UserCreateDTO) -> UserViewModel:
        """Create a new user with all related entities in a single transaction"""
        # Hash passwords
        entity.password = self._hash_password(dto.password)
        entity.confirm_password = self._hash_password(dto.confirm_password)

        # ========== Validations ==========
        # Validate passwords
        self._validate_passwords(dto.password, dto.confirm_password)
        
        # Check if document already exists
        existing = await self.repository.get_by_document(dto.document)
        if existing:
            raise ValueError("Documento pertence a outra pessoa")
        
        # Check if email already exists
        if dto.email:
            existing_email = await self.repository.get_by_email(dto.email)
            if existing_email:
                raise ValueError("E-mail pertence a outra pessoa")
        
        # Check if cellphone already exists
        if dto.cellphone_number:
            existing_phone = await self.repository.get_by_cellphone(dto.cellphone_number)
            if existing_phone:
                raise ValueError("Número de celular pertence a outra pessoa")
        
        # ========== Business Rules ==========
        is_student = dto.user_type_id == 5 # Student
        is_over_70 = (DateTimeHandler.now().date() - dto.birthdate).days > 70 * 365
        
        # Rule 1: Students must have legal_representative_1
        if is_student and not dto.legal_representative_1:
            raise ValueError("Students must have at least one legal representative")
        
        # Rule 2: Users over 70 must have health certificate
        if is_over_70 and not dto.health_certificate:
            raise ValueError("Users over 70 must provide a health certificate")
        
        # ========== Create User ==========
        # Convert DTO -> Entity
        entity = DtoToEntityMapper.user(dto)
        
        # Business rule: Validate age (must be at least 16)
        if entity.age < 16:
            raise ValueError("User must be at least 16 years old")
        
        # Convert Entity -> Model and save
        model = EntityToModelMapper.user(entity)
        saved_model = await self.repository.create(model)
        user_id = UUID(bytes=saved_model.id)
        user_id_bytes = saved_model.id
        
        # ========== Save Password History ==========
        await self.password_history_service.add_password_hash_to_history(
            user_id=user_id,
            hashed_password=dto.password
        )
        
        # ========== Create Documents ==========
        # Helper to create document
        async def _create_document(doc_dto, user_id_bytes, legal_rep_id_bytes=None):
            """Create a document record"""
            doc_entity = DtoToEntityMapper.document(doc_dto)
            doc_entity.user_id = UUID(bytes=user_id_bytes)
            if legal_rep_id_bytes:
                doc_entity.legal_representative_id = UUID(bytes=legal_rep_id_bytes)
            doc_model = EntityToModelMapper.document(doc_entity)
            return await self.document_repo.create(doc_model)
        
        # ID Document Front
        await _create_document(dto.id_document_front, user_id_bytes)
        
        # ID Document Back
        await _create_document(dto.id_document_back, user_id_bytes)
        
        # User Photo
        await _create_document(dto.user_photo, user_id_bytes)
        
        # Health Certificate (if over 70 or provided)
        if dto.health_certificate:
            await _create_document(dto.health_certificate, user_id_bytes)
        
        # ========== Create Address ==========
        address_entity = DtoToEntityMapper.address(dto.address)
        address_entity.user_id = user_id
        address_model = EntityToModelMapper.address(address_entity)
        await self.address_repo.create(address_model)
        
        # ========== Create Legal Representatives (for students) ==========
        async def _create_legal_representative(rep_dto, student_user_id_bytes):
            """Create a legal representative with documents"""
            # Create representative
            rep_entity = DtoToEntityMapper.legal_representative(rep_dto)
            rep_entity.user_id = UUID(bytes=student_user_id_bytes)
            
            # Check if representative document already exists
            existing_rep = await self.legal_rep_repo.get_by_document(rep_dto.document)
            if existing_rep:
                raise ValueError(f"Legal representative document {rep_dto.document} already registered")
            
            rep_model = EntityToModelMapper.legal_representative(rep_entity)
            saved_rep = await self.legal_rep_repo.create(rep_model)
            rep_id_bytes = saved_rep.id
            
            # Create ID document for representative
            await _create_document(rep_dto.id_document, user_id_bytes, rep_id_bytes)
            
            # Create student registry authorization (document_type_id = 5)
            await _create_document(rep_dto.student_registry_authorization, user_id_bytes, rep_id_bytes)
            
            return saved_rep
        
        if dto.legal_representative_1:
            await _create_legal_representative(dto.legal_representative_1, user_id_bytes)
        
        if dto.legal_representative_2:
            await _create_legal_representative(dto.legal_representative_2, user_id_bytes)
        
        # ========== Return ViewModel ==========
        saved_entity = ModelToEntityMapper.user(saved_model)

        return EntityToViewModelMapper.user(saved_entity)
    
    async def update_user(self, user_id: UUID, dto: UserUpdateDTO) -> UserViewModel:
        """Update user with business validation"""
        model = await self.repository.get_by_id(user_id)
        if not model:
            raise ValueError("User not found")
        
        # Check email uniqueness if being updated
        if dto.email:
            existing = await self.repository.get_by_email(dto.email)
            if existing and existing.id != model.id:
                raise ValueError("Email already registered")
        
        # Check cellphone uniqueness if being updated
        if dto.cellphone_number:
            existing = await self.repository.get_by_cellphone(dto.cellphone_number)
            if existing and existing.id != model.id:
                raise ValueError("Cellphone already registered")
        
        # Convert to entity and apply updates
        entity = ModelToEntityMapper.user(model)
        updated_entity = UpdateMapper.user(entity, dto)
        
        # Save changes
        updated_model = EntityToModelMapper.user(updated_entity)
        saved_model = await self.repository.update(updated_model)
        
        saved_entity = ModelToEntityMapper.user(saved_model)
        return EntityToViewModelMapper.user(saved_entity)
    
    async def authenticate(self, dto: UserLoginDTO) -> Optional[UserViewModel]:
        """Authenticate user with document and password"""
        user = await self.repository.get_by_document(dto.document)
        if not user:
            return None
        
        if not user.active:
            raise ValueError("User account is deactivated")
        
        if not self._verify_password(dto.password, user.password):
            return None
        
        entity = ModelToEntityMapper.user(user)
        return EntityToViewModelMapper.user(entity)
    
    async def change_password(self, user_id: UUID, dto: PasswordChangeDTO) -> bool:
        """Change user password with validation"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not self._verify_password(dto.current_password, user.password):
            raise ValueError("Current password is incorrect")
        
        # Validate new password against history
        validation = await self.password_history_service.validate_password_change(
            user_id=user_id,
            new_plain_password=dto.new_password,
            history_check_count=5
        )
        
        if not validation['valid']:
            raise ValueError(validation['reason'])
        
        # Hash and update password
        hashed_password = self._hash_password(dto.new_password)
        success = await self.repository.update_password(user_id, hashed_password)
        
        if success:
            # Add to password history
            await self.password_history_service.add_password_hash_to_history(
                user_id=user_id,
                hashed_password=hashed_password
            )
        
        return success
    
    async def deactivate_user(self, user_id: UUID, reason: Optional[str] = None) -> bool:
        """Deactivate user account"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.active:
            raise ValueError("User already deactivated")
        
        # Business rule: Check if user has active enrollments
        # This would require enrollment repository
        
        return await self.repository.deactivate(user_id)
    
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.active:
            raise ValueError("User already active")
        
        return await self.repository.activate(user_id)
    
    async def find_users(
        self,
        name: Optional[str] = None,
        document: Optional[str] = None,
        email: Optional[str] = None,
        phoneNumber: Optional[str] = None,
        user_type_id: Optional[int] = None,
        active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """Find users with filters and pagination"""
        skip = (page - 1) * page_size
        
        models = await self.repository.find_by_filters(
            name=name,
            document=document,
            email=email,
            phoneNumber=phoneNumber,
            user_type_id=user_type_id,
            active=active,
            skip=skip,
            limit=page_size
        )
        
        total = await self.repository.count({
            'active': active,
            'user_type_id': user_type_id
        })
        
        entities = [ModelToEntityMapper.user(model) for model in models]
        view_models = [EntityToViewModelMapper.user(entity) for entity in entities]
        
        return {
            'items': view_models,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    async def get_educators(self, page: int = 1, page_size: int = 10) -> dict:
        """Get all educators"""
        skip = (page - 1) * page_size
        models = await self.repository.get_educators(skip, page_size)
        
        entities = [ModelToEntityMapper.user(model) for model in models]
        view_models = [EntityToViewModelMapper.user(entity) for entity in entities]
        
        return {
            'items': view_models,
            'page': page,
            'page_size': page_size
        }
    
    async def get_students(self, page: int = 1, page_size: int = 10) -> dict:
        """Get all students"""
        skip = (page - 1) * page_size
        models = await self.repository.get_students(skip, page_size)
        
        entities = [ModelToEntityMapper.user(model) for model in models]
        view_models = [EntityToViewModelMapper.user(entity) for entity in entities]
        
        return {
            'items': view_models,
            'page': page,
            'page_size': page_size
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    async def _save_password_history(self, user_id: bytes, hashed_password: str) -> None:
        """Save password to history"""
        from src.domain.entities.user_password_history import UserPasswordHistory
        from uuid import uuid4
        
        history = UserPasswordHistory(
            id=uuid4(),
            created_at=DateTimeHandler.now(),
            password=hashed_password,
            user_id=user_id
        )
        
        history_model = EntityToModelMapper.user_password_history(history)
        await self.password_history_repo.create(history_model)

    def _validate_passwords(self, password: str, confirm_password: str) -> None:
        """
        Validate if passwords match and password strength requirements:
        - 8 to 128 characters
        - At least one lowercase letter
        - At least one uppercase letter
        - At least one number
        - At least one special character
        """
        import re

        if password != confirm_password:
            raise ValueError("As senhas são diferentes")
        
        # Check length
        if len(password) < 8:
            raise ValueError("A senha deve conter pelo menos 8 caracteres")
        
        if len(password) > 128:
            raise ValueError("A senha deve conter no máximo 128 caracteres")
        
        # Check lowercase
        if not re.search(r'[a-z]', password):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula")
        
        # Check uppercase
        if not re.search(r'[A-Z]', password):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        
        # Check number
        if not re.search(r'\d', password):
            raise ValueError("A senha deve conter pelo menos um número")
        
        # Check special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/\'`~]', password):
            raise ValueError("A senha deve conter pelo menos um caractere especial")