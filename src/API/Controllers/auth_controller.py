"""Authentication controller"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.application.services.auth_service import AuthService
from src.data.repositories.user_repository import UserRepository
from src.data.db_context.database import get_db
from sqlalchemy.orm import Session

from src.domain.dtos.auth_dto import LoginDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)

@router.post("/login")
async def login(
    body: LoginDTO,
    service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return tokens"""
    result = await service.authenticate(body)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return result

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    result = await service.refresh_access_token(refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return result