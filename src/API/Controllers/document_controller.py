"""Document controller"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.application.services.document_service import DocumentService
from src.application.services.document_validation_service import DocumentValidationService
from src.data.repositories.document_repository import DocumentRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.data.repositories.document_validation_repository import DocumentValidationRepository
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.dtos.document_validation_dto import DocumentValidationDTO
from src.domain.view_models.document_validation_view_model import DocumentValidationViewModel
from src.domain.view_models.document_view_model import DocumentViewModel
from src.domain.entities.user import User

router = APIRouter(
    prefix="/document",
    tags=["Document"],
    dependencies=[Depends(get_current_active_user)]
)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    """Dependency injection for DocumentService"""
    repository = DocumentRepository(db)
    return DocumentService(repository)
    
    
def get_validation_service(db: Session = Depends(get_db)) -> DocumentValidationService:
    """Dependency injection for DocumentValidationService"""
    repository = DocumentValidationRepository(db)
    return DocumentValidationService(repository)


@router.post("/", response_model=DocumentViewModel, status_code=status.HTTP_201_CREATED)
async def upload_document(
    dto: DocumentCreateDTO,
    current_user: User = Depends(get_current_active_user),
    service: DocumentService = Depends(get_document_service)
):
    """Upload a new document."""
    try:
        return await service.upload_document(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[DocumentViewModel])
async def get_user_documents(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DocumentService = Depends(get_document_service)
):
    """
    Get all documents for a user.
    - Admin/Secretary can view any user's documents
    - Users can view their own documents
    """
    if current_user.user_type_id not in [1, 2] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own documents")
    
    return await service.get_user_documents(user_id)


@router.get("/{document_id}", response_model=DocumentViewModel)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID."""
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if current_user.user_type_id not in [1, 2] and document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only view your own documents")
    
    return document


@router.get("/{document_id}/download")
async def download_document(
    request: Request,
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DocumentService = Depends(get_document_service)
):
    """Download a document."""
    try:
        user_ip = request.client.host if request.client else "unknown"
        result = await service.get_document_for_download(
            document_id,
            current_user.id,
            user_ip
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Document validation
@router.put("/{document_id}/validate", response_model=DocumentValidationViewModel)
async def validate_document(
    request: Request,
    document_id: UUID,
    dto: DocumentValidationDTO,
    current_user: User = Depends(get_current_active_user),
    service: DocumentValidationService = Depends(get_validation_service)
):
    """
    Validate a document (create or update validation).
    Admin (1) and Secretary (2) only.
    """
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can validate documents")
    
    try:
        user_ip = request.client.host if request.client else "unknown"
        return await service.create_or_update_validation(
            dto=dto,
            document_id=document_id,
            performed_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/validate/pending", response_model=list[DocumentValidationViewModel])
async def get_pending_validations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Get pending document validations."""
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can list documents")
    return await service.get_pending_validations(skip, limit)