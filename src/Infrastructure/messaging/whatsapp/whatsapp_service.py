"""WhatsApp service for sending messages via WhatsApp Business API"""
from typing import Optional, List
import requests

from src.infrastructure.configuration.settings import config

class WhatsAppService:
    """Service for sending WhatsApp messages"""
    
    def __init__(self):
        self.api_url = config.get("WhatsApp.ApiUrl", "")
        self.phone_number_id = config.get("WhatsApp.PhoneNumber", "")
        self.access_token = config.get("WhatsApp.AccessToken", "")
        self.from_number = config.get("WhatsApp.FromNumber", "")
    
    async def send_whatsapp(
        self,
        to_phone: str,
        message: str,
        document_1_base64: Optional[str] = None,
        document_2_base64: Optional[str] = None
    ) -> bool:
        """
        Send WhatsApp message with optional documents.
        
        Args:
            to_phone: Recipient phone number (international format)
            message: Text message
            document_1_base64: Optional first document (image/pdf)
            document_2_base64: Optional second document (image/pdf)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Send text message first
            text_sent = await self._send_whatsapp_text(to_phone, message)
            
            # Send documents if provided
            doc1_sent = True
            doc2_sent = True
            
            if document_1_base64:
                doc1_sent = await self._send_whatsapp_document(to_phone, document_1_base64)
            
            if document_2_base64:
                doc2_sent = await self._send_whatsapp_document(to_phone, document_2_base64)
            
            return text_sent and doc1_sent and doc2_sent
            
        except Exception as e:
            print(f"Failed to send WhatsApp message: {e}")
            return False
    
    async def _send_whatsapp_text(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp text message"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Failed to send WhatsApp text: {e}")
            return False
    
    async def _send_whatsapp_document(self, to_phone: str, base64_content: str) -> bool:
        """Send WhatsApp document/image"""
        try:
            import base64
            import tempfile
            import os
            
            # Determine media type from base64 header if present
            media_type = "image/png"
            if base64_content.startswith("data:"):
                header, base64_content = base64_content.split(",", 1)
                media_type = header.split(":")[1].split(";")[0]
            
            # Decode base64
            file_data = base64.b64decode(base64_content)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name
            
            # Upload media
            url = f"{self.api_url}/{self.phone_number_id}/media"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            with open(tmp_path, "rb") as f:
                files = {"file": f}
                form_data = {"messaging_product": "whatsapp", "type": media_type}
                response = requests.post(url, files=files, data=form_data, headers=headers)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            if response.status_code != 200:
                return False
            
            media_id = response.json().get("id")
            
            # Send document message
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "document",
                "document": {"id": media_id, "caption": "Documento"}
            }
            
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Failed to send WhatsApp document: {e}")
            return False