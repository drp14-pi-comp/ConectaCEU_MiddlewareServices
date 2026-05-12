"""User sex type repository"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.data.models.user_sex_type_model import UserSexTypeModel
from src.data.repositories.base.base_repository import BaseRepository

class UserSexTypeRepository(BaseRepository):
    """Repository for User Sex Type reference entity"""
    
    def __init__(self, session: Session):
        super().__init__(session, UserSexTypeModel)
    
    async def get_by_description(self, description: str) -> Optional[UserSexTypeModel]:
        """Get sex type by description"""
        stmt = select(UserSexTypeModel).where(UserSexTypeModel.description == description)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()