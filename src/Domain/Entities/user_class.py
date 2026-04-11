"""User class enrollment domain entity"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserClass(BaseModel):
    """User class enrollment domain entity"""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    active: bool = True
    user_id: UUID
    class_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
    
    def deactivate(self) -> None:
        """Deactivate enrollment"""
        self.active = False
        self.updated_at = datetime.now()