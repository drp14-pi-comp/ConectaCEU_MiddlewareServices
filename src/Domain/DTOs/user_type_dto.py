"""DTOs for User Type operations"""
from typing import Optional
from pydantic import BaseModel, Field

class UserTypeCreateDTO(BaseModel):
    """DTO for creating a user type"""
    description: str = Field(..., min_length=3, max_length=50)
    register_user: bool = False
    validate_user_documents: bool = False
    list_secretaries: bool = False
    list_educators: bool = False
    list_students: bool = False
    send_broadcast_message: bool = False
    add_courses: bool = False
    add_classes: bool = False
    emit_user_documents: bool = False

class UserTypeUpdateDTO(BaseModel):
    """DTO for updating a user type"""
    description: Optional[str] = Field(None, min_length=3, max_length=50)
    register_user: Optional[bool] = None
    validate_user_documents: Optional[bool] = None
    list_secretaries: Optional[bool] = None
    list_educators: Optional[bool] = None
    list_students: Optional[bool] = None
    send_broadcast_message: Optional[bool] = None
    add_courses: Optional[bool] = None
    add_classes: Optional[bool] = None
    emit_user_documents: Optional[bool] = None
    
    def get_non_none_fields(self) -> dict:
        """Return only fields that are not None"""
        return {k: v for k, v in self.model_dump().items() if v is not None}