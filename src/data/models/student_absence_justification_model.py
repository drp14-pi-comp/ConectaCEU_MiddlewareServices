"""Student absence justification model - Links an attendance record to a justifying document"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkBaseModel

class StudentAbsenceJustificationModel(UuidPkBaseModel):
    __tablename__ = "student_absence_justification"

    class_attendance_id = Column(BINARY(16), ForeignKey('class_attendance.id'), nullable=False)
    document_id = Column(BINARY(16), ForeignKey('document.id'), nullable=False)

    def get_uuid(self):
        return super().get_uuid()