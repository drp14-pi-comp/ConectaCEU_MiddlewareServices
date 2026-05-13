"""Profiles to exclude model - Tracks users excluded from specific processes"""
from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from src.data.db_context.base import UuidPkBaseModel

class ProfilesToExcludeModel(UuidPkBaseModel):
    __tablename__ = "profiles_to_exclude"

    processed = Column(Boolean, nullable=False, default=False)

    user_id = Column(BINARY(16), ForeignKey('user.id'), nullable=False)

    def get_uuid(self):
        return super().get_uuid()