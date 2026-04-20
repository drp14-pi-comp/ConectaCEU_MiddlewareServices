"""Password reset service - handles forgot password flow"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4
import secrets

from src.data.repositories.user_repository import UserRepository
from src.application.services.user_password_history_service import UserPasswordHistoryService
from src.infrastructure.email.email_service import EmailService
from src.infrastructure.configuration.settings import config

class PasswordResetService:
    """Service for password reset flow"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        password_history_service: UserPasswordHistoryService,
        email_service: EmailService
    ):
        self.user_repo = user_repo
        self.password_history_service = password_history_service
        self.email_service = email_service
    
    async def request_password_reset(self, email: str) -> dict:
        """
        Request password reset by email and document.
        Generates reset token and sends email.
        
        Args:
            email: User's email
            
        Returns:
            Dict with status message
        """
        # Find user by email
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Don't reveal if user exists or not (security)
            return {"message": "If the information matches, a reset email will be sent"}
        
        # Check if user is active
        if not user.active:
            return {"message": "If the information matches, a reset email will be sent"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.now(datetime.timezone.utc) + timedelta(hours=1)
        
        # Save token to user
        user.password_reset_token = reset_token
        user.password_reset_expires = token_expiry
        await self.user_repo.update(user)
        
        # Send email
        frontend_url = config.get("App.FrontendUrl", "http://localhost:3000")
        await self.email_service.send_password_reset_email(
            to_email=user.email,
            user_name=user.name,
            reset_token=reset_token,
            frontend_url=frontend_url
        )
        
        return {"message": "If the information matches, a reset email will be sent"}
    
    async def request_password_reset_by_document(self, document: str) -> dict:
        """
        Request password reset by document only.
        Sends email to user's registered email.
        
        Args:
            document: User's document (CPF)
            
        Returns:
            Dict with status message
        """
        # Find user by document
        user = await self.user_repo.get_by_document(document)
        if not user:
            return {"message": "If the document is registered, a reset email will be sent"}
        
        if not user.active:
            return {"message": "If the document is registered, a reset email will be sent"}
        
        if not user.email:
            return {"message": "No email registered for this document"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.now(datetime.timezone.utc) + timedelta(hours=1)
        
        # Save token to user
        user.password_reset_token = reset_token
        user.password_reset_expires = token_expiry
        await self.user_repo.update(user)
        
        # Send email
        frontend_url = config.get("App.FrontendUrl", "http://localhost:3000")
        await self.email_service.send_password_reset_email(
            to_email=user.email,
            user_name=user.name,
            reset_token=reset_token,
            frontend_url=frontend_url
        )
        
        return {"message": "If the document is registered, a reset email will be sent"}
    
    async def validate_reset_token(self, token: str) -> dict:
        """
        Validate password reset token.
        
        Args:
            token: Reset token from email
            
        Returns:
            Dict with validation result
        """
        # Find user by reset token
        user = await self.user_repo.find_by_password_reset_token(token)
        if not user:
            return {"valid": False, "reason": "Invalid or expired token"}
        
        # Check if token is expired
        if user.password_reset_expires and user.password_reset_expires < datetime.now(datetime.timezone.utc):
            return {"valid": False, "reason": "Token has expired"}
        
        return {
            "valid": True,
            "user_id": str(UUID(bytes=user.id)),
            "message": "Token is valid"
        }
    
    async def reset_password(self, token: str, new_password: str) -> dict:
        """
        Reset password using token.
        
        Args:
            token: Reset token from email
            new_password: New plain text password
            
        Returns:
            Dict with result status
        """
        # Validate token
        validation = await self.validate_reset_token(token)
        if not validation["valid"]:
            return {"success": False, "reason": validation["reason"]}
        
        user_id = UUID(validation["user_id"])
        user = await self.user_repo.get_by_id(user_id)
        
        # Validate password strength
        if len(new_password) < 8:
            return {"success": False, "reason": "Password must be at least 8 characters"}
        
        # Check password history
        validation_result = await self.password_history_service.validate_password_change(
            user_id=user_id,
            new_plain_password=new_password,
            history_check_count=5
        )
        
        if not validation_result["valid"]:
            return {"success": False, "reason": validation_result["reason"]}
        
        # Hash and update password
        from src.application.services.auth_service import AuthService
        auth_service = AuthService(self.user_repo)
        hashed_password = auth_service._hash_password(new_password)
        
        success = await self.user_repo.update_password(user_id, hashed_password)
        
        if success:
            # Add to password history
            await self.password_history_service.add_password_hash_to_history(
                user_id=user_id,
                hashed_password=hashed_password
            )
            
            # Clear reset token
            user.password_reset_token = None
            user.password_reset_expires = None
            await self.user_repo.update(user)
            
            return {"success": True, "message": "Password reset successfully"}
        
        return {"success": False, "reason": "Failed to update password"}