"""Document validation controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.document_validation_service import DocumentValidationService
from src.data.repositories.document_validation_repository import DocumentValidationRepository
from src.data.db_context.database import get_db
from src.domain.dtos.document_validation_dto import DocumentValidationCreateDTO, DocumentValidationUpdateDTO
from src.domain.view_models.document_validation_view_model import DocumentValidationViewModel

router = APIRouter(prefix="/validation", tags=["Document Validation"])

def get_validation_service(db: Session = Depends(get_db)) -> DocumentValidationService:
    repository = DocumentValidationRepository(db)
    return DocumentValidationService(repository)

@router.post("/", response_model=DocumentValidationViewModel, status_code=status.HTTP_201_CREATED)
async def create_validation(
    dto: DocumentValidationCreateDTO,
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Create a document validation (pending status)"""
    try:
        return await service.create_validation(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pending", response_model=list[DocumentValidationViewModel])
async def get_pending_validations(
    skip: int = 0,
    limit: int = 100,
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Get pending document validations"""
    return await service.get_pending_validations(skip, limit)

@router.get("/document/{document_id}", response_model=DocumentValidationViewModel)
async def get_validation_by_document(
    document_id: UUID,
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Get validation for a document"""
    try:
        return await service.get_validation_by_document(document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{validation_id}", response_model=DocumentValidationViewModel)
async def update_validation(
    validation_id: UUID,
    dto: DocumentValidationUpdateDTO,
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Update a document validation (approve/reject)"""
    try:
        return await service.update_validation(validation_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{validation_id}/approve")
async def approve_document(
    validation_id: UUID,
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Approve a document"""
    try:
        return await service.approve_document(validation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{validation_id}/reject")
async def reject_document(
    validation_id: UUID,
    reason: str,
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Reject a document with reason"""
    try:
        return await service.reject_document(validation_id, reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))