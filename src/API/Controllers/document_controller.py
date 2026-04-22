"""Document controller"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from src.application.services.document_service import DocumentService
from src.data.repositories.document_repository import DocumentRepository
from src.data.db_context.database import get_db
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.view_models.document_view_model import DocumentViewModel

router = APIRouter(prefix="/document", tags=["Document"])

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository)

@router.post("/", response_model=DocumentViewModel, status_code=status.HTTP_201_CREATED)
async def upload_document(
    dto: DocumentCreateDTO,
    service: DocumentService = Depends(get_document_service)
):
    """Upload a new document"""
    try:
        return await service.upload_document(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[DocumentViewModel])
async def get_user_documents(
    user_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get all documents for a user"""
    return await service.get_user_documents(user_id)

@router.get("/user/{user_id}/type/{document_type_id}", response_model=List[DocumentViewModel])
async def get_documents_by_type(
    user_id: UUID,
    document_type_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get documents of specific type for a user"""
    return await service.get_documents_by_type(user_id, document_type_id)

@router.get("/{document_id}", response_model=DocumentViewModel)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID"""
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document