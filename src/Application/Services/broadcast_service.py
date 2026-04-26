"""Broadcast message service - sends messages to multiple recipients"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.data.repositories.user_repository import UserRepository
from src.data.repositories.user_class_repository import UserClassRepository
from src.data.repositories.log_broadcast_message_repository import LogBroadcastMessageRepository
from src.infrastructure.messaging.email.email_service import EmailService
from src.infrastructure.messaging.sms.sms_service import SmsService
from src.infrastructure.messaging.whatsapp.whatsapp_service import WhatsAppService
from src.domain.dtos.broadcast_message_dto import BroadcastMessageCreateDTO

class BroadcastService:
    """Service for sending broadcast messages via multiple channels"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        user_class_repo: UserClassRepository,
        log_repo: LogBroadcastMessageRepository,
        email_service: EmailService,
        sms_service: SmsService,
        whatsapp_service: WhatsAppService
    ):
        self.user_repo = user_repo
        self.user_class_repo = user_class_repo
        self.log_repo = log_repo
        self.email_service = email_service
        self.sms_service = sms_service
        self.whatsapp_service = whatsapp_service
    
    async def send_broadcast(
        self,
        dto: BroadcastMessageCreateDTO,
        sender_user_id: UUID,
        sender_ip_address: str
    ) -> dict:
        """
        Send broadcast message to recipients via selected channels.
        """
        # Extract documents from list (max 2)
        document_1 = dto.documents[0] if len(dto.documents) > 0 else None
        document_2 = dto.documents[1] if len(dto.documents) > 1 else None
        
        results = {
            'email_sent': 0,
            'email_failed': 0,
            'whatsapp_sent': 0,
            'whatsapp_failed': 0,
            'sms_sent': 0,
            'sms_failed': 0,
            'total_processed': 0,
            'total_errors': 0
        }
        
        async for user in self._stream_recipients(
            dto.recipient_user_ids,
            dto.recipient_course_id,
            dto.recipient_user_type_id
        ):
            try:
                results['total_processed'] += 1
                
                # Send email
                if dto.send_email and user.email:
                    try:
                        email_sent = await self.email_service.send_broadcast_email(
                            to_email=user.email,
                            subject="ConectaCEU - Comunicado",
                            message=self._format_html_message(dto.message),
                            document_1_base64=document_1,
                            document_2_base64=document_2
                        )
                        
                        if email_sent:
                            results['email_sent'] += 1
                        else:
                            results['email_failed'] += 1
                    except Exception:
                        results['email_failed'] += 1
                
                # Send WhatsApp
                if dto.send_whatsapp and user.cellphone_number:
                    try:
                        whatsapp_sent = await self.whatsapp_service.send_whatsapp(
                            to_phone=user.cellphone_number,
                            message=dto.message,
                            document_1_base64=document_1,
                            document_2_base64=document_2
                        )
                        
                        if whatsapp_sent:
                            results['whatsapp_sent'] += 1
                        else:
                            results['whatsapp_failed'] += 1
                    except Exception:
                        results['whatsapp_failed'] += 1
                
                # Send SMS
                if dto.send_sms and user.cellphone_number:
                    try:
                        sms_sent = await self.sms_service.send_sms(
                            to_phone=user.cellphone_number,
                            message=dto.message[:160]
                        )
                        
                        if sms_sent:
                            results['sms_sent'] += 1
                        else:
                            results['sms_failed'] += 1
                    except Exception:
                        results['sms_failed'] += 1
                        
            except Exception:
                results['total_errors'] += 1
        
        # Log the broadcast
        await self.log_repo.log_broadcast(
            message=dto.message,
            document_1_base64=document_1 or "",
            document_2_base64=document_2 or "",
            sent_whatsapp=dto.send_whatsapp and results['whatsapp_sent'] > 0,
            sent_email=dto.send_email and results['email_sent'] > 0,
            sent_sms=dto.send_sms and results['sms_sent'] > 0,
            user_id=sender_user_id.bytes,
            user_ip_address=sender_ip_address
        )
        
        return results
    
    async def _get_recipients(
        self,
        user_ids: Optional[List[str]] = None,
        course_id: Optional[str] = None,
        user_type_id: Optional[int] = None
    ) -> List:
        """Get recipients based on filters"""
        recipients = []
        seen_ids = set()
        
        # By specific user IDs
        if user_ids:
            for user_id_str in user_ids:
                user_id = UUID(user_id_str)
                user = await self.user_repo.get_by_id(user_id)
                if user and user.active and user.id not in seen_ids:
                    recipients.append(user)
                    seen_ids.add(user.id)
        
        # By course (all enrolled students)
        if course_id:
            course_uuid = UUID(course_id)
            # Get all components for this course
            from src.data.repositories.course_component_repository import CourseComponentRepository
            component_repo = CourseComponentRepository(self.user_repo.session)
            components = await component_repo.get_by_course_id(course_uuid)
            
            for component in components:
                from src.data.repositories.class_repository import ClassRepository
                class_repo = ClassRepository(self.user_repo.session)
                classes = await class_repo.get_by_component_id(UUID(bytes=component.id))
                
                for class_ in classes:
                    enrollments = await self.user_class_repo.get_active_by_class_id(UUID(bytes=class_.id))
                    for enrollment in enrollments:
                        user = await self.user_repo.get_by_id(UUID(bytes=enrollment.user_id))
                        if user and user.active and user.id not in seen_ids:
                            recipients.append(user)
                            seen_ids.add(user.id)
        
        # By user type
        if user_type_id:
            users = await self.user_repo.find_by_filters(user_type_id=user_type_id, active=True)
            for user in users:
                if user.id not in seen_ids:
                    recipients.append(user)
                    seen_ids.add(user.id)
        
        return recipients
    
    def _format_html_message(self, message: str) -> str:
        """Format message as HTML for email"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;">Comunicado ConectaCEU</h2>
                    <div style="background: #f9f9f9; padding: 20px; border-radius: 5px;">
                        <p style="white-space: pre-wrap;">{message}</p>
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        Esta é uma mensagem automática do sistema ConectaCEU. Favor não responder.
                    </p>
                </div>
            </body>
        </html>
        """