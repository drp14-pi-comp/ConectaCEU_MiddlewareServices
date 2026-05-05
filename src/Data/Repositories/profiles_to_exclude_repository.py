from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.data.models.profiles_to_exclude_model import ProfilesToExcludeModel
from src.data.repositories.base.base_repository import BaseRepository

class ProfilesToExcludeRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, ProfilesToExcludeModel)

    async def get_by_user_id(self, user_id: UUID) -> Optional[ProfilesToExcludeModel]:
        """Check if a user's profile is on the exclusion list."""
        stmt = select(ProfilesToExcludeModel).where(ProfilesToExcludeModel.user_id == user_id.bytes)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_excluded_users(self, skip: int = 0, limit: int = 100) -> List[ProfilesToExcludeModel]:
        """Get a paginated list of all excluded profiles."""
        stmt = select(ProfilesToExcludeModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())