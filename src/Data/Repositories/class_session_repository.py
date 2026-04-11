"""Class session repository"""
from typing import List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.data.models.class_session_model import ClassSessionModel
from src.data.repositories.base.base_repository import BaseRepository

class ClassSessionRepository(BaseRepository[ClassSessionModel]):
    """Repository for Class Session entity"""
    
    def __init__(self, session: Session):
        super().__init__(session, ClassSessionModel)
    
    async def get_by_class_id(self, class_id: UUID) -> List[ClassSessionModel]:
        """Get all sessions for a class"""
        stmt = select(ClassSessionModel).where(
            ClassSessionModel.class_id == class_id.bytes
        ).order_by(ClassSessionModel.date)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_date_range(
        self,
        class_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[ClassSessionModel]:
        """Get sessions in date range"""
        stmt = select(ClassSessionModel).where(
            ClassSessionModel.class_id == class_id.bytes,
            ClassSessionModel.date >= start_date,
            ClassSessionModel.date <= end_date
        ).order_by(ClassSessionModel.date)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_upcoming_sessions(self, class_id: UUID) -> List[ClassSessionModel]:
        """Get future sessions for a class"""
        stmt = select(ClassSessionModel).where(
            ClassSessionModel.class_id == class_id.bytes,
            ClassSessionModel.date > datetime.utcnow()
        ).order_by(ClassSessionModel.date)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_past_sessions(self, class_id: UUID) -> List[ClassSessionModel]:
        """Get past sessions for a class"""
        stmt = select(ClassSessionModel).where(
            ClassSessionModel.class_id == class_id.bytes,
            ClassSessionModel.date < datetime.utcnow()
        ).order_by(ClassSessionModel.date.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())