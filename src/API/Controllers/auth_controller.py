"""Authentication controller"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.application.services.auth_service import AuthService
from src.application.services.user_password_history_service import UserPasswordHistoryService
from src.application.services.user_service import UserService
from src.data.repositories.address_repository import AddressRepository
from src.data.repositories.document_repository import DocumentRepository
from src.data.repositories.legal_representative_repository import LegalRepresentativeRepository
from src.data.repositories.user_password_history_repository import UserPasswordHistoryRepository
from src.data.repositories.user_repository import UserRepository
from src.data.db_context.database import get_db
from sqlalchemy.orm import Session

from src.domain.dtos.auth_dto import LoginDTO
from src.domain.dtos.user_dto import UserCreateDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    user_repo = UserRepository(db)
    password_history_repo = UserPasswordHistoryRepository(db)
    password_history_service = UserPasswordHistoryService(password_history_repo)
    document_repo = DocumentRepository(db)
    address_repo = AddressRepository(db)
    legal_rep_repo = LegalRepresentativeRepository(db)
    return UserService(
        user_repo,
        password_history_service,
        document_repo,
        address_repo,
        legal_rep_repo
    )

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

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def public_register(
    dto: UserCreateDTO,
    service: UserService = Depends(get_user_service)
):
    """
    Public registration. User is created inactive.
    Documents need validation by a Secretary.
    """
    try:
        user = await service.create_user(
            dto,
            created_by_user_id=None  # Public registration
        )
        return {
            "message": "Cadastro bem-sucedido. Sua conta será ativada após validação da documentação.",
            "user_id": str(user.id)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))