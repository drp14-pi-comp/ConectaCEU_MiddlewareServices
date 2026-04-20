"""User password history service - business logic for User Password History entity"""
from typing import List
from uuid import UUID
import bcrypt

from src.data.repositories.user_password_history_repository import UserPasswordHistoryRepository
from src.application.services.base_service import BaseService
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper
from src.domain.view_models.user_password_history_view_model import UserPasswordHistoryViewModel

class UserPasswordHistoryService(BaseService):
    """Service for User Password History business logic"""
    
    def __init__(self, repository: UserPasswordHistoryRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_user_password_history(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> List[UserPasswordHistoryViewModel]:
        """Get password history for a user"""
        models = await self.repository.get_by_user_id(user_id, skip, limit)
        entities = [ModelToEntityMapper.user_password_history(model) for model in models]
        return [EntityToViewModelMapper.user_password_history(entity) for entity in entities]
    
    async def get_recent_passwords(self, user_id: UUID, limit: int = 5) -> List[UserPasswordHistoryViewModel]:
        """Get recent password history for a user"""
        models = await self.repository.get_recent_by_user_id(user_id, limit)
        entities = [ModelToEntityMapper.user_password_history(model) for model in models]
        return [EntityToViewModelMapper.user_password_history(entity) for entity in entities]
    
    async def is_password_reused(
        self,
        user_id: UUID,
        plain_password: str,
        check_count: int = 5
    ) -> bool:
        """
        Check if a plain password matches any recent password in history.
        
        Args:
            user_id: The user's ID
            plain_password: The plain text password to check
            check_count: Number of recent passwords to check (default: 5)
            
        Returns:
            True if password was recently used, False otherwise
        """
        # Get recent password history
        recent_history = await self.repository.get_recent_by_user_id(user_id, check_count)
        
        # Check each historical password against the plain password
        for history_entry in recent_history:
            if self._verify_password(plain_password, history_entry.password):
                return True
        
        return False
    
    async def is_password_hash_reused(
        self,
        user_id: UUID,
        password_hash: str,
        check_count: int = 5
    ) -> bool:
        """
        Check if a password hash matches any recent password in history.
        Use this when you already have the hashed password.
        
        Args:
            user_id: The user's ID
            password_hash: The hashed password to check
            check_count: Number of recent passwords to check (default: 5)
            
        Returns:
            True if hash was recently used, False otherwise
        """
        return await self.repository.is_password_reused(user_id, password_hash, check_count)
    
    async def add_password_to_history(
        self,
        user_id: UUID,
        plain_password: str
    ) -> UserPasswordHistoryViewModel:
        """
        Hash a plain password and add it to the user's password history.
        
        Args:
            user_id: The user's ID
            plain_password: The plain text password to hash and store
            
        Returns:
            The created password history entry
        """
        # Hash the password before storing
        hashed_password = self._hash_password(plain_password)
        
        # Create password history entry
        from uuid import uuid4
        from datetime import datetime
        from src.domain.entities.user_password_history import UserPasswordHistory
        from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
        
        entity = UserPasswordHistory(
            id=uuid4(),
            created_at=datetime.utcnow(),
            password=hashed_password,
            user_id=user_id
        )
        
        model = EntityToModelMapper.user_password_history(entity)
        saved_model = await self.repository.create(model)
        saved_entity = ModelToEntityMapper.user_password_history(saved_model)
        
        # Cleanup old passwords (keep only last 10)
        await self.cleanup_old_passwords(user_id, max_history=10)
        
        return EntityToViewModelMapper.user_password_history(saved_entity)
    
    async def add_password_hash_to_history(
        self,
        user_id: UUID,
        hashed_password: str
    ) -> UserPasswordHistoryViewModel:
        """
        Add an already hashed password to the user's password history.
        Use this when the password is already hashed (e.g., during user creation).
        
        Args:
            user_id: The user's ID
            hashed_password: The already hashed password
            
        Returns:
            The created password history entry
        """
        from uuid import uuid4
        from datetime import datetime
        from src.domain.entities.user_password_history import UserPasswordHistory
        from src.application.mappers.entity_to_model_mapper import EntityToModelMapper
        
        entity = UserPasswordHistory(
            id=uuid4(),
            created_at=datetime.utcnow(),
            password=hashed_password,
            user_id=user_id
        )
        
        model = EntityToModelMapper.user_password_history(entity)
        saved_model = await self.repository.create(model)
        saved_entity = ModelToEntityMapper.user_password_history(saved_model)
        
        # Cleanup old passwords (keep only last 10)
        await self.cleanup_old_passwords(user_id, max_history=10)
        
        return EntityToViewModelMapper.user_password_history(saved_entity)
    
    async def validate_password_change(
        self,
        user_id: UUID,
        new_plain_password: str,
        history_check_count: int = 5
    ) -> dict:
        """
        Validate a password change against history rules.
        
        Args:
            user_id: The user's ID
            new_plain_password: The new plain text password
            history_check_count: Number of recent passwords to check against
            
        Returns:
            Dict with validation results: {'valid': bool, 'reason': str}
        """
        # Check minimum length
        if len(new_plain_password) < 8:
            return {'valid': False, 'reason': 'Password must be at least 8 characters'}
        
        # Check maximum length
        if len(new_plain_password) > 100:
            return {'valid': False, 'reason': 'Password must be at most 100 characters'}
        
        # Check for password reuse
        is_reused = await self.is_password_reused(user_id, new_plain_password, history_check_count)
        if is_reused:
            return {'valid': False, 'reason': f'Password was used in the last {history_check_count} passwords'}
        
        return {'valid': True, 'reason': 'Password is valid'}
    
    async def cleanup_old_passwords(self, user_id: UUID, max_history: int = 10) -> int:
        """
        Clean up old password entries, keeping only the most recent ones.
        
        Args:
            user_id: The user's ID
            max_history: Maximum number of password history entries to keep
            
        Returns:
            Number of deleted entries
        """
        return await self.repository.cleanup_old_passwords(user_id, max_history)
    
    async def get_password_history_count(self, user_id: UUID) -> int:
        """Get count of password history entries for a user"""
        return await self.repository.count_by_user_id(user_id)
    
    async def clear_password_history(self, user_id: UUID) -> int:
        """
        Clear all password history for a user.
        Use with caution - typically only for testing or admin operations.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Number of deleted entries
        """
        count = await self.repository.count_by_user_id(user_id)
        await self.cleanup_old_passwords(user_id, max_history=0)
        return count
    
    def _hash_password(self, plain_password: str) -> str:
        """
        Hash a plain password using bcrypt.
        
        Args:
            plain_password: The plain text password
            
        Returns:
            The hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')
    
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
    
    async def get_password_age_summary(self, user_id: UUID) -> dict:
        """
        Get password age summary for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dict with password age information
        """
        recent = await self.repository.get_recent_by_user_id(user_id, limit=1)
        
        if not recent:
            return {
                'has_history': False,
                'current_password_age_days': None,
                'total_historical_passwords': 0
            }
        
        from datetime import datetime
        current_password = recent[0]
        age = (datetime.utcnow() - current_password.created_at).days
        
        total = await self.repository.count_by_user_id(user_id)
        
        return {
            'has_history': True,
            'current_password_age_days': age,
            'total_historical_passwords': total,
            'last_changed': current_password.created_at
        }