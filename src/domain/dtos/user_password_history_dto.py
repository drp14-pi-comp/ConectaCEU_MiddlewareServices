"""DTOs for User Password History operations"""
from pydantic import BaseModel, Field

class PasswordHistoryFilterDTO(BaseModel):
    """DTO for filtering password history"""
    user_id: str  # UUID as string
    limit: int = Field(10, ge=1, le=100)