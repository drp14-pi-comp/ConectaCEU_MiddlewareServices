"""User service - business logic for User entity"""
from typing import Optional
from uuid import UUID
import bcrypt

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
    
    def __init__(self, repository: UserRepository, password_history_repo: UserPasswordHistoryRepository):
        super().__init__(repository)
        self.repository = repository
        self.password_history_repo = password_history_repo
    
    async def create_user(self, dto: UserCreateDTO) -> UserViewModel:
        """Create a new user with business validation"""
        # Check if document already exists
        existing = await self.repository.get_by_document(dto.document)
        if existing:
            raise ValueError("Document already registered")
        
        # Check if email already exists
        if dto.email:
            existing_email = await self.repository.get_by_email(dto.email)
            if existing_email:
                raise ValueError("Email already registered")
        
        # Check if cellphone already exists
        if dto.cellphone_number:
            existing_phone = await self.repository.get_by_cellphone(dto.cellphone_number)
            if existing_phone:
                raise ValueError("Cellphone already registered")
        
        # Validate password strength
        if len(dto.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Convert DTO -> Entity
        entity = DtoToEntityMapper.user(dto)
        
        # Business rule: Validate age (must be at least 16)
        if entity.age < 16:
            raise ValueError("User must be at least 16 years old")
        
        # Hash password
        hashed_password = self._hash_password(dto.password)
        entity.password = hashed_password
        
        # Convert Entity -> Model and save
        model = EntityToModelMapper.user(entity)
        saved_model = await self.repository.create(model)
        
        # Save to password history
        await self.password_history_service.add_password_hash_to_history(
            user_id=UUID(bytes=saved_model.id),
            hashed_password=hashed_password
        )
        
        # Convert back to ViewModel
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