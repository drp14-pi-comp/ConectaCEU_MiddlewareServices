"""Broadcast message controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.application.services.broadcast_service import BroadcastService
from src.data.repositories.user_repository import UserRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.log_broadcast_message_repository import LogBroadcastMessageRepository
from src.infrastructure.messaging.email.email_service import EmailService
from src.infrastructure.messaging.sms.sms_service import SmsService
from src.infrastructure.messaging.whatsapp.whatsapp_service import WhatsAppService
from src.data.db_context.database import get_db
from src.domain.dtos.broadcast_message_dto import BroadcastMessageCreateDTO
from src.domain.entities.user import User

router = APIRouter(prefix="/broadcasts", tags=["Broadcasts"])


def get_broadcast_service(db: Session = Depends(get_db)) -> BroadcastService:
    """Dependency injection for BroadcastService"""
    user_repo = UserRepository(db)
    user_class_repo = UserClassRepository(db)
    log_repo = LogBroadcastMessageRepository(db)
    email_service = EmailService()
    sms_service = SmsService()
    whatsapp_service = WhatsAppService()
    
    return BroadcastService(
        user_repo,
        user_class_repo,
        log_repo,
        email_service,
        sms_service,
        whatsapp_service
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def send_broadcast(
    request: Request,
    dto: BroadcastMessageCreateDTO,
    current_user_id: str,
    service: BroadcastService = Depends(get_broadcast_service)
):
    """Send a broadcast message via selected channels"""
    try:
        sender_ip = request.client.host if request.client else "unknown"
        result = await service.send_broadcast(dto, UUID(current_user_id), sender_ip)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))