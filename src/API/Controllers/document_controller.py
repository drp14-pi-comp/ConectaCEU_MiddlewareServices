"""Document controller"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.application.services.document_service import DocumentService
from src.data.repositories.document_repository import DocumentRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.dtos.document_dto import DocumentCreateDTO
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


@router.get("/user/{user_id}/type/{document_type_id}", response_model=List[DocumentViewModel])
async def get_documents_by_type(
    user_id: UUID,
    document_type_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DocumentService = Depends(get_document_service)
):
    """
    Get documents of specific type for a user.
    - Admin/Secretary can view any user's documents
    - Users can view their own documents
    """
    if current_user.user_type_id not in [1, 2] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own documents")
    
    return await service.get_documents_by_type(user_id, document_type_id)


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
    """Download a document (logs the request)."""
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