"""Base models for different entity types"""
import uuid
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """Abstract base"""
    __abstract__ = True

class IntPkBaseModel(BaseModel):
    """Base for entities with Integer auto-increment PK"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)

class UuidPkBaseModel(BaseModel):
    """
    Base for entities with UUID/Binary(16) PK
    - Includes creation date column
    """
    __abstract__ = True
    
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def get_uuid(self) -> uuid.UUID:
        """Convert binary ID back to UUID"""
        return uuid.UUID(bytes=self.id)
    
    @staticmethod
    def uuid_to_binary(uuid_obj: uuid.UUID) -> bytes:
        """Convert UUID to binary for queries"""
        return uuid_obj.bytes

class UuidPkUpdatableBaseModel(BaseModel):
    """
    Base for entities with UUID/Binary(16) PK
    - Includes audit columns
    """
    __abstract__ = True
    
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def get_uuid(self) -> uuid.UUID:
        """Convert binary ID back to UUID"""
        return uuid.UUID(bytes=self.id)
    
    @staticmethod
    def uuid_to_binary(uuid_obj: uuid.UUID) -> bytes:
        """Convert UUID to binary for queries"""
        return uuid_obj.bytes
    
class LogBaseModel(BaseModel):
    """Base for log tables"""
    __abstract__ = True
    
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def get_uuid(self) -> uuid.UUID:
        """Convert binary ID back to UUID"""
        return uuid.UUID(bytes=self.id)