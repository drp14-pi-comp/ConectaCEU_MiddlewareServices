"""Address controller"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.address_service import AddressService
from src.data.repositories.address_repository import AddressRepository
from src.data.db_context.database import get_db
from src.domain.dtos.address_dto import AddressCreateDTO, AddressUpdateDTO
from src.domain.view_models.address_view_model import AddressViewModel

router = APIRouter(prefix="/address", tags=["Address"])

def get_address_service(db: Session = Depends(get_db)) -> AddressService:
    repository = AddressRepository(db)
    return AddressService(repository)

@router.post("/", response_model=AddressViewModel, status_code=status.HTTP_201_CREATED)
async def create_address(
    dto: AddressCreateDTO,
    service: AddressService = Depends(get_address_service)
):
    """Create a new address"""
    try:
        return await service.create_address(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[AddressViewModel])
async def get_user_addresses(
    user_id: UUID,
    service: AddressService = Depends(get_address_service)
):
    """Get all addresses for a user"""
    return await service.get_user_addresses(user_id)

@router.get("/{address_id}", response_model=AddressViewModel)
async def get_address(
    address_id: UUID,
    service: AddressService = Depends(get_address_service)
):
    """Get address by ID"""
    address = await service.get_by_id(address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.put("/{address_id}", response_model=AddressViewModel)
async def update_address(
    address_id: UUID,
    dto: AddressUpdateDTO,
    service: AddressService = Depends(get_address_service)
):
    """Update an address"""
    try:
        address = await service.update_address(address_id, dto)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        return address
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))