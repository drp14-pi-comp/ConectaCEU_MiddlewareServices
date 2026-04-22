"""Password reset controller"""
from fastapi import APIRouter, HTTPException, status

from src.application.services.password_reset_service import PasswordResetService
from src.domain.dtos.user_dto import PasswordResetRequestDTO, PasswordResetDTO

router = APIRouter(prefix="/password", tags=["Password Reset"])

@router.get("/reset/validate")
async def validate_reset_token(
    token: str,
    service: PasswordResetService
):
    """Validate password reset token"""
    result = await service.validate_reset_token(token)
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["reason"])
    return result

@router.post("/reset")
async def reset_password(
    request: PasswordResetDTO,
    service: PasswordResetService
):
    """Reset password using token"""
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    result = await service.reset_password(request.token, request.new_password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["reason"])
    
    return {"message": result["message"]}