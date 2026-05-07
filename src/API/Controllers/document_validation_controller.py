"""Document validation controller"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.application.services.document_validation_service import DocumentValidationService
from src.data.repositories.document_validation_repository import DocumentValidationRepository
from src.data.db_context.database import get_db
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.dtos.document_validation_dto import DocumentValidationDTO
from src.domain.view_models.document_validation_view_model import DocumentValidationViewModel
from src.domain.entities.user import User

router = APIRouter(
    prefix="/validation",
    tags=["Document Validation"],
    dependencies=[Depends(get_current_active_user)]
)


def get_validation_service(db: Session = Depends(get_db)) -> DocumentValidationService:
    """Dependency injection for DocumentValidationService"""
    repository = DocumentValidationRepository(db)
    return DocumentValidationService(repository)


@router.put("/document/{document_id}", response_model=DocumentValidationViewModel)
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


@router.patch("/document/{document_id}/approve")
async def approve_document(
    request: Request,
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DocumentValidationService = Depends(get_validation_service)
):
    """
    Approve a document. Admin (1) and Secretary (2) only.
    """
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can approve documents")
    
    try:
        user_ip = request.client.host if request.client else "unknown"
        dto = DocumentValidationDTO(
            document_validation_status_type_id=2,
            rejection_reason=None
        )
        return await service.create_or_update_validation(
            dto=dto,
            document_id=document_id,
            performed_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/document/{document_id}/reject")
async def reject_document(
    request: Request,
    document_id: UUID,
    reason: str,
    current_user: User = Depends(get_current_active_user),
    service: DocumentValidationService = Depends(get_validation_service)
):
    """
    Reject a document with reason. Admin (1) and Secretary (2) only.
    """
    if current_user.user_type_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Only administrators and secretaries can reject documents")
    
    try:
        user_ip = request.client.host if request.client else "unknown"
        dto = DocumentValidationDTO(
            document_validation_status_type_id=3,
            rejection_reason=reason
        )
        return await service.create_or_update_validation(
            dto=dto,
            document_id=document_id,
            performed_by_user_id=current_user.id,
            user_ip_address=user_ip
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pending", response_model=list[DocumentValidationViewModel])
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


@router.get("/document/{document_id}", response_model=DocumentValidationViewModel)
async def get_validation_by_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DocumentValidationService = Depends(get_validation_service)
):
    """Get validation for a document."""
    try:
        if current_user.user_type_id not in [1, 2]:
            raise HTTPException(status_code=403, detail="Only administrators and secretaries can list documents")
        return await service.get_validation_by_document(document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))