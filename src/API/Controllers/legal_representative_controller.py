"""Legal representative controller"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.legal_representative_service import LegalRepresentativeService
from src.data.repositories.legal_representative_repository import LegalRepresentativeRepository
from src.data.db_context.database import get_db
from src.domain.dtos.legal_representative_dto import LegalRepresentativeCreateDTO, LegalRepresentativeUpdateDTO
from src.domain.view_models.legal_representative_view_model import LegalRepresentativeViewModel

router = APIRouter(prefix="/representative", tags=["Legal Representative"])

def get_representative_service(db: Session = Depends(get_db)) -> LegalRepresentativeService:
    repository = LegalRepresentativeRepository(db)
    return LegalRepresentativeService(repository)

@router.post("/", response_model=LegalRepresentativeViewModel, status_code=status.HTTP_201_CREATED)
async def create_representative(
    dto: LegalRepresentativeCreateDTO,
    service: LegalRepresentativeService = Depends(get_representative_service)
):
    """Create a new legal representative"""
    try:
        return await service.create_representative(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[LegalRepresentativeViewModel])
async def get_user_representatives(
    user_id: UUID,
    service: LegalRepresentativeService = Depends(get_representative_service)
):
    """Get all legal representatives for a user"""
    return await service.get_user_representatives(user_id)

@router.get("/{representative_id}", response_model=LegalRepresentativeViewModel)
async def get_representative(
    representative_id: UUID,
    service: LegalRepresentativeService = Depends(get_representative_service)
):
    """Get representative by ID"""
    representative = await service.get_by_id(representative_id)
    if not representative:
        raise HTTPException(status_code=404, detail="Representative not found")
    return representative

@router.put("/{representative_id}", response_model=LegalRepresentativeViewModel)
async def update_representative(
    representative_id: UUID,
    dto: LegalRepresentativeUpdateDTO,
    service: LegalRepresentativeService = Depends(get_representative_service)
):
    """Update a legal representative"""
    try:
        representative = await service.update_representative(representative_id, dto)
        if not representative:
            raise HTTPException(status_code=404, detail="Representative not found")
        return representative
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{representative_id}")
async def delete_representative(
    representative_id: UUID,
    service: LegalRepresentativeService = Depends(get_representative_service)
):
    """Delete a legal representative"""
    deleted = await service.delete(representative_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Representative not found")
    return {"message": "Representative deleted successfully"}