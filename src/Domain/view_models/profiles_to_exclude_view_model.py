"""ProfilesToExclude ViewModel"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ProfilesToExcludeViewModel(BaseModel):
    id: UUID
    created_at: datetime
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)