"""Class repository"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.data.models.class_model import ClassModel
from src.data.repositories.base.base_repository import BaseRepository

class ClassRepository(BaseRepository[ClassModel]):
    """Repository for Class entity"""
    
    def __init__(self, session: Session):
        super().__init__(session, ClassModel)
    
    async def get_by_component_id(self, component_id: UUID) -> List[ClassModel]:
        """Get all classes for a component"""
        stmt = select(ClassModel).where(ClassModel.component_id == component_id.bytes)
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_active_by_component_id(self, component_id: UUID) -> List[ClassModel]:
        """Get all active classes for a component"""
        stmt = select(ClassModel).where(
            ClassModel.component_id == component_id.bytes,
            ClassModel.active == True
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def find_by_filters(
        self,
        component_id: Optional[UUID] = None,
        shift_type_id: Optional[int] = None,
        active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClassModel]:
        """Find classes with filters"""
        conditions = []
        
        if component_id:
            conditions.append(ClassModel.component_id == component_id.bytes)
        if shift_type_id:
            conditions.append(ClassModel.shift_type_id == shift_type_id)
        if active is not None:
            conditions.append(ClassModel.active == active)
        
        stmt = select(ClassModel)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.offset(skip).limit(limit)
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def increment_seats(self, class_id: UUID) -> bool:
        """Increment seats in use"""
        class_ = await self.get_by_id(class_id)
        if class_:
            class_.seats_in_use += 1
            self.session.flush()
            return True
        return False
    
    async def decrement_seats(self, class_id: UUID) -> bool:
        """Decrement seats in use"""
        class_ = await self.get_by_id(class_id)
        if class_ and class_.seats_in_use > 0:
            class_.seats_in_use -= 1
            self.session.flush()
            return True
        return False
    
    async def deactivate(self, class_id: UUID) -> bool:
        """Deactivate class"""
        class_ = await self.get_by_id(class_id)
        if class_:
            class_.active = False
            self.session.flush()
            return True
        return False