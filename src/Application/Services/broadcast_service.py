"""Broadcast message service - sends messages to multiple recipients"""
from typing import AsyncGenerator, List, Optional
from uuid import UUID

from src.application.logging.application_logger import ApplicationLogger
from src.data.models.user_class_model import UserClassModel
from src.data.models.user_model import UserModel
from src.data.repositories.class_repository import ClassRepository
from src.data.repositories.course_component_repository import CourseComponentRepository
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
        component_repo: CourseComponentRepository,
        class_repo: ClassRepository,
        email_service: EmailService,
        sms_service: SmsService,
        whatsapp_service: WhatsAppService
    ):
        self.user_repo = user_repo
        self.user_class_repo = user_class_repo
        self.log_repo = log_repo
        self.component_repo = component_repo
        self.class_repo = class_repo
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
        try:
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
            await self.log_repo.log(
                message=dto.message,
                document_1_base64=document_1 or "",
                document_2_base64=document_2 or "",
                sent_whatsapp=dto.send_whatsapp and results['whatsapp_sent'] > 0,
                sent_email=dto.send_email and results['email_sent'] > 0,
                sent_sms=dto.send_sms and results['sms_sent'] > 0,
                user_id=sender_user_id.bytes,
                user_ip_address=sender_ip_address
            )
            self.log_repo.session.commit()
            
            return results
        except Exception as e:
            await ApplicationLogger.log_error(e, reraise=True)
    
    async def _stream_recipients(
        self,
        user_ids: Optional[List[str]] = None,
        course_id: Optional[str] = None,
        user_type_id: Optional[int] = None
    ) -> AsyncGenerator[UserModel]:
        """
        Stream recipients one at a time from different sources.
        Yields one user at a time to avoid loading all into memory.
        """
        seen_ids = set()

        # If no filters, stream all active users
        if not user_ids and not course_id and not user_type_id:
            yield self._stream_all_users(seen_ids)
            return
        
        # By specific user IDs
        if user_ids:
            yield self._stream_by_user_ids(seen_ids, user_ids)
            return
        
        # By course - stream through enrollments
        if course_id:
            yield self._stream_by_course_id(seen_ids, UUID(course_id))
            return
        
        # By user type
        if user_type_id:
            yield self._stream_by_user_type_id(seen_ids, user_type_id)
            return
            

    async def _stream_all_users(self, seen_ids: set) -> AsyncGenerator[UserModel, None]:
        """Stream all active users in batches."""
        page_size = 100
        page = 0
        
        while True:
            users = await self.user_repo.find_by_filters(
                active=True,
                skip=page * page_size,
                limit=page_size
            )
            
            if not users:
                break
            
            for user in users:
                if user.id not in seen_ids:
                    seen_ids.add(user.id)
                    yield user
            
            page += 1

    async def _stream_by_user_ids(self, seen_ids: set, user_ids: List[str]) -> AsyncGenerator[UserModel, None]:
        """Stream all active users by their IDs."""
        while True:
            for user_id_str in user_ids:
                user_id = UUID(user_id_str)
                user = await self.user_repo.get_by_id(user_id)
                if user and user.active and user.id not in seen_ids:
                    seen_ids.add(user.id)
                    yield user

    async def _stream_by_course_id(self, seen_ids: set, course_uuid: UUID) -> AsyncGenerator[UserModel, None]:
        components = await self.component_repo.get_by_course_id(course_uuid)
            
        for component in components:
            component_uuid = UUID(bytes=component.id)
            
            # Get classes for this component
            classes = await self.class_repo.get_by_component_id(component_uuid)
            
            for class_ in classes:
                class_uuid = UUID(bytes=class_.id)
                
                # Stream active enrollments one at a time
                async for enrollment in self._stream_enrollments(class_uuid):
                    user = await self.user_repo.get_by_id(UUID(bytes=enrollment.user_id))
                    if user and user.active and user.id not in seen_ids:
                        seen_ids.add(user.id)
                        yield user

    async def _stream_enrollments(self, class_id: UUID) -> AsyncGenerator[UserClassModel]:
        """Stream active enrollments for a class"""
        page_size = 100
        page = 0
        
        while True:
            enrollments = await self.user_class_repo.get_active_by_class_id(
                class_id, 
                skip=page * page_size,
                limit=page_size
            )
            
            if not enrollments:
                break
            
            for enrollment in enrollments:
                yield enrollment
            
            page += 1


    async def _stream_by_user_type_id(self, seen_ids: set, user_type_id: int):
        page_size = 100  # Process in batches
        page = 0
        
        while True:
            users = await self.user_repo.find_by_filters(
                user_type_id=user_type_id,
                active=True,
                skip=page * page_size,
                limit=page_size
            )
            
            if not users:
                break
            
            for user in users:
                if user.id not in seen_ids:
                    seen_ids.add(user.id)
                    yield user
            
            page += 1
    
    
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