"""SMS service for sending text messages"""
from typing import Optional
import requests

from src.infrastructure.configuration.settings import settings

class SmsService:
    """Service for sending SMS messages"""
    
    def __init__(self):
        self.api_url = settings.SMS_API_URL
        self.api_key = settings.SMS_API_KEY
        self.from_number = settings.SMS_FROM_NUMBER
    
    async def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> bool:
        """
        Send SMS to a phone number.
        
        Args:
            to_phone: Recipient phone number
            message: Message content
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Example using a generic SMS API
            response = requests.post(
                self.api_url,
                json={
                    "to": to_phone,
                    "from": self.from_number,
                    "message": message
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False