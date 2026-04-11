"""User class enrollment repository"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_

from src.data.models.user_class_model import UserClassModel
from src.data.repositories.base.base_repository import BaseRepository

class UserClassRepository(BaseRepository[UserClassModel]):
    """Repository for User Class enrollment entity"""
    
    def __init__(self, session: Session):
        super().__init__(session, UserClassModel)
    
    async def get_by_user_id(self, user_id: UUID) -> List[UserClassModel]:
        """Get all enrollments for a user"""
        stmt = select(UserClassModel).where(UserClassModel.user_id == user_id.bytes)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_active_by_user_id(self, user_id: UUID) -> List[UserClassModel]:
        """Get active enrollments for a user"""
        stmt = select(UserClassModel).where(
            UserClassModel.user_id == user_id.bytes,
            UserClassModel.active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_class_id(self, class_id: UUID) -> List[UserClassModel]:
        """Get all enrollments for a class"""
        stmt = select(UserClassModel).where(UserClassModel.class_id == class_id.bytes)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_active_by_class_id(self, class_id: UUID) -> List[UserClassModel]:
        """Get active enrollments for a class"""
        stmt = select(UserClassModel).where(
            UserClassModel.class_id == class_id.bytes,
            UserClassModel.active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user_and_class(self, user_id: UUID, class_id: UUID) -> Optional[UserClassModel]:
        """Get enrollment for specific user and class"""
        stmt = select(UserClassModel).where(
            UserClassModel.user_id == user_id.bytes,
            UserClassModel.class_id == class_id.bytes
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def deactivate_enrollment(self, enrollment_id: UUID) -> bool:
        """Deactivate enrollment"""
        enrollment = await self.get_by_id(enrollment_id)
        if enrollment:
            enrollment.active = False
            await self.session.flush()
            return True
        return False
    
    async def activate_enrollment(self, enrollment_id: UUID) -> bool:
        """Activate enrollment"""
        enrollment = await self.get_by_id(enrollment_id)
        if enrollment:
            enrollment.active = True
            await self.session.flush()
            return True
        return False
    
    async def count_active_by_class_id(self, class_id: UUID) -> int:
        """Count active enrollments in a class"""
        stmt = select(func.count()).select_from(UserClassModel).where(
            UserClassModel.class_id == class_id.bytes,
            UserClassModel.active == True
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0