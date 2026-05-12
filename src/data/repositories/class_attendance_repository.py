"""Class attendance repository"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import Integer, select, and_, func

from src.data.models.class_attendance_model import ClassAttendanceModel
from src.data.repositories.base.base_repository import BaseRepository

class ClassAttendanceRepository(BaseRepository[ClassAttendanceModel]):
    """Repository for Class Attendance entity"""
    
    def __init__(self, session: Session):
        super().__init__(session, ClassAttendanceModel)
    
    async def get_by_session_id(self, session_id: UUID) -> List[ClassAttendanceModel]:
        """Get all attendance records for a session"""
        stmt = select(ClassAttendanceModel).where(
            ClassAttendanceModel.class_session_id == session_id.bytes
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[ClassAttendanceModel]:
        """Get all attendance records for a user"""
        stmt = select(ClassAttendanceModel).where(
            ClassAttendanceModel.user_id == user_id.bytes
        ).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user_and_session(self, user_id: UUID, session_id: UUID) -> Optional[ClassAttendanceModel]:
        """Get attendance record for specific user and session"""
        stmt = select(ClassAttendanceModel).where(
            ClassAttendanceModel.user_id == user_id.bytes,
            ClassAttendanceModel.class_session_id == session_id.bytes
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def mark_attendance(self, attendance_id: UUID, attended: bool) -> bool:
        """Mark attendance as present/absent"""
        attendance = await self.get_by_id(attendance_id)
        if attendance:
            attendance.attended = attended
            self.session.flush()
            return True
        return False
    
    async def bulk_create(self, attendances: List[ClassAttendanceModel]) -> List[ClassAttendanceModel]:
        """Create multiple attendance records at once"""
        self.session.add_all(attendances)
        self.session.flush()
        return attendances
    
    async def get_attendance_summary(self, session_id: UUID) -> dict:
        """Get attendance summary for a session"""
        stmt = select(
            func.count().label('total'),
            func.sum(ClassAttendanceModel.attended.cast(Integer)).label('present')
        ).where(ClassAttendanceModel.class_session_id == session_id.bytes)
        
        result = self.session.execute(stmt)
        row = result.first()
        
        total = row.total or 0
        present = row.present or 0
        
        return {
            'total': total,
            'present': present,
            'absent': total - present,
            'attendance_rate': (present / total * 100) if total > 0 else 0
        }
    
    async def get_user_attendance_summary(self, user_id: UUID, class_id: UUID) -> dict:
        """Get attendance summary for a user in a specific class"""
        from src.data.models.class_session_model import ClassSessionModel
        
        stmt = select(
            func.count().label('total'),
            func.sum(ClassAttendanceModel.attended.cast(Integer)).label('present')
        ).join(
            ClassSessionModel,
            ClassAttendanceModel.class_session_id == ClassSessionModel.id
        ).where(
            ClassAttendanceModel.user_id == user_id.bytes,
            ClassSessionModel.class_id == class_id.bytes
        )
        
        result = self.session.execute(stmt)
        row = result.first()
        
        total = row.total or 0
        present = row.present or 0
        
        return {
            'total_sessions': total,
            'attended': present,
            'missed': total - present,
            'attendance_rate': (present / total * 100) if total > 0 else 0
        }