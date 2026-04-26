"""Email service for sending notifications"""
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.infrastructure.configuration.settings import config

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = config.get("Email.SmtpHost", "smtp.gmail.com")
        self.smtp_port = config.get("Email.SmtpPort", 587)
        self.smtp_user = config.get("Email.SmtpUser", "")
        self.smtp_password = config.get("Email.SmtpPassword", "")
        self.from_email = config.get("Email.FromEmail", "noreply@conectaceu.com")
        self.from_name = config.get("Email.FromName", "ConectaCEU")
    
    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str,
        frontend_url: str
    ) -> bool:
        """
        Send password reset email with reset link.
        
        Args:
            to_email: Recipient email
            user_name: User's name
            reset_token: Password reset token
            frontend_url: Frontend base URL
            
        Returns:
            True if email sent successfully
        """
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "ConectaCEU - Password Reset Request"
        
        html_content = f"""
        <html>
            <body>
                <h2>Pedido de troca de senha</h2>
                <p>Olá {user_name},</p>
                <p>Recebemos um pedido de troca de senha da sua conta ConectaCEU.</p>
                <p>Clique no link abaixo para trocar sua senha:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>O link expirará em 1 (uma) hora.</p>
                <p>Se você não pediu a troca, por favor ignore este e-mail.</p>
                <p>Atenciosamente,<br>Equipe ConectaCEU</p>
            </body>
        </html>
        """
        
        text_content = f"""
        Pedido de troca de senha
        
        Olá {user_name},
        
        Recebemos um pedido de troca de senha da sua conta ConectaCEU.
        
        Copie e cole este link no seu navegador para trocar sua senha:
        {reset_link}
        
        O link expirará em 1 (uma) hora.
        
        Se você não pediu a troca, por favor ignore este e-mail.
        
        Atenciosamente,
        Equipe ConectaCEU
        """
        
        return await self._send_email(to_email, subject, html_content, text_content)
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False