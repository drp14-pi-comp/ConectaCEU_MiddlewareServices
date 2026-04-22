"""Authentication service - JWT token management and user authentication"""
from datetime import timedelta
from typing import Optional
from uuid import UUID
import bcrypt
from jose import jwt, JWTError

from src.infrastructure.configuration.settings import config
from src.data.repositories.user_repository import UserRepository
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.domain.entities.user import User
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

class AuthService:
    """Service for authentication and JWT token management"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_access_token(self, user_id: UUID, user_type_id: int) -> str:
        """Create JWT access token"""
        expire = DateTimeHandler.now() + timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(user_id),
            "user_type_id": user_type_id,
            "exp": expire,
            "iat": DateTimeHandler.now()
        }
        
        return jwt.encode(payload, config.settings.SECRET_KEY, algorithm=config.settings.JWT_ALGORITHM)
    
    def create_refresh_token(self, user_id: UUID) -> str:
        """Create JWT refresh token"""
        expire = DateTimeHandler.now() + timedelta(days=config.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": DateTimeHandler.now(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, config.settings.SECRET_KEY, algorithm=config.settings.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                config.settings.SECRET_KEY,
                algorithms=[config.settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user_model = await self.user_repo.get_by_id(UUID(user_id))
        if not user_model:
            return None
        
        return ModelToEntityMapper.user(user_model)
    
    async def authenticate(self, document: str, password: str) -> Optional[dict]:
        """
        Authenticate user with document and password.
        
        Args:
            document: User's document (CPF)
            password: Plain text password
            
        Returns:
            Dict with tokens if authentication successful, None otherwise
        """
        # Find user by document
        user = await self.user_repo.get_by_document(document)
        if not user:
            return None
        
        # Check if user is active
        if not user.active:
            return None
        
        # Verify password
        if not self._verify_password(password, user.password):
            return None
        
        # Check if account is locked
        if hasattr(user, 'locked_until') and user.locked_until:
            if user.locked_until > DateTimeHandler.now():
                return None
        
        # Generate tokens
        user_uuid = UUID(bytes=user.id)
        access_token = self.create_access_token(user_uuid, user.user_type_id)
        refresh_token = self.create_refresh_token(user_uuid)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": config.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user_uuid),
                "name": user.name,
                "email": user.email,
                "user_type_id": user.user_type_id
            }
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict with new tokens if successful, None otherwise
        """
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.active:
            return None
        
        # Create new tokens
        access_token = self.create_access_token(UUID(user_id), user.user_type_id)
        new_refresh_token = self.create_refresh_token(UUID(user_id))
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": config.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def validate_credentials(self, document: str, password: str) -> dict:
        """
        Validate user credentials without generating tokens.
        Useful for password change validation or pre-authentication checks.
        
        Args:
            document: User's document (CPF)
            password: Plain text password
            
        Returns:
            Dict with validation result
        """
        user = await self.user_repo.get_by_document(document)
        if not user:
            return {'valid': False, 'reason': 'User not found'}
        
        if not user.active:
            return {'valid': False, 'reason': 'User is deactivated'}
        
        if not self._verify_password(password, user.password):
            return {'valid': False, 'reason': 'Invalid password'}
        
        return {
            'valid': True,
            'user_id': str(UUID(bytes=user.id)),
            'user_type_id': user.user_type_id
        }
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False