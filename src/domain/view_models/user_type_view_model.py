"""User type view model"""
from pydantic import BaseModel, ConfigDict

class UserTypeViewModel(BaseModel):
    id: int
    description: str
    register_user: bool
    validate_user_documents: bool
    list_secretaries: bool
    list_educators: bool
    list_students: bool
    send_broadcast_message: bool
    add_courses: bool
    add_classes: bool
    emit_user_documents: bool
    
    model_config = ConfigDict(from_attributes=True)