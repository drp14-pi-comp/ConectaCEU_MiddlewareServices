"""User type domain entity with permissions"""
from pydantic import BaseModel, ConfigDict

class UserType(BaseModel):
    """User type reference entity with permissions"""
    id: int
    description: str
    register_user: bool = False
    validate_user_documents: bool = False
    list_secretaries: bool = False
    list_educators: bool = False
    list_students: bool = False
    send_broadcast_message: bool = False
    add_courses: bool = False
    add_classes: bool = False
    emit_user_documents: bool = False
    
    model_config = ConfigDict(from_attributes=True)