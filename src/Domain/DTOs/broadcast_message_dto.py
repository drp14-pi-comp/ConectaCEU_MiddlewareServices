"""DTOs for Broadcast Message operations"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class BroadcastMessageCreateDTO(BaseModel):
    """DTO for creating a broadcast message"""
    message: str = Field(..., min_length=1, max_length=4000)
    
    # Documents as a list (max 2)
    documents: List[str] = Field(
        default_factory=list,
        max_length=2,
        description="Optional documents as base64 strings (max 2)"
    )
    
    # Delivery channels
    send_email: bool = False
    send_whatsapp: bool = False
    send_sms: bool = False
    
    # Recipients
    recipient_user_ids: Optional[List[str]] = None  # Specific users
    recipient_course_id: Optional[str] = None  # All students in a course
    recipient_user_type_id: Optional[int] = None  # All users of a type
    
    @field_validator('documents')
    def validate_documents(cls, v: List[str]) -> List[str]:
        """Validate document list"""
        # Check max quantity
        if len(v) > 2:
            raise ValueError('Maximum of 2 documents allowed')
        
        # Validate each document
        for i, doc in enumerate(v):
            if not doc:
                raise ValueError(f'Document {i+1} cannot be empty')
            
            # Limit to ~10MB for scalability
            max_length = 10_000_000  # 10MB in base64
            if len(doc) > max_length:
                raise ValueError(f'Document {i+1} exceeds maximum size of 10MB')
        
        return v
    
    @field_validator('message')
    def validate_message_not_empty(cls, v: str) -> str:
        """Message must not be empty"""
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()