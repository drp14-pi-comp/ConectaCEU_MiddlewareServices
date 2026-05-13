"""ProfilesToExclude domain entity"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ProfilesToExclude(BaseModel):
    """Represents a user profile that is excluded from certain lists or operations."""
    id: UUID
    created_at: datetime
    processed: bool
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)