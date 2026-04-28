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
from src.api.dependencies.auth_dependencies import get_current_active_user
from src.domain.entities.user import User

router = APIRouter(
    prefix="/address",
    tags=["Address"],
    dependencies=[Depends(get_current_active_user)]
)


def get_address_service(db: Session = Depends(get_db)) -> AddressService:
    """Dependency injection for AddressService"""
    repository = AddressRepository(db)
    return AddressService(repository)


@router.post("/", response_model=AddressViewModel, status_code=status.HTTP_201_CREATED)
async def create_address(
    dto: AddressCreateDTO,
    current_user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service)
):
    """
    Create a new address.
    All authenticated users can create addresses (their own).
    """
    try:
        return await service.create_address(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[AddressViewModel])
async def get_user_addresses(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service)
):
    """
    Get all addresses for a user.
    - Users can view their own addresses
    - Admin/Secretary can view any user's addresses
    - Others: 403
    """
    # Admin (1) and Secretary (2) can view any
    if current_user.user_type_id in [1, 2]:
        return await service.get_user_addresses(user_id)
    
    # Users can only view their own
    if current_user.id == user_id:
        return await service.get_user_addresses(user_id)
    
    raise HTTPException(status_code=403, detail="Can only view your own addresses")


@router.get("/{address_id}", response_model=AddressViewModel)
async def get_address(
    address_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service)
):
    """Get address by ID"""
    address = await service.get_by_id(address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Admin/Secretary can view any
    if current_user.user_type_id in [1, 2]:
        return address
    
    # Users can only view their own
    if address.user_id == current_user.id:
        return address
    
    raise HTTPException(status_code=403, detail="Can only view your own addresses")


@router.put("/{address_id}", response_model=AddressViewModel)
async def update_address(
    address_id: UUID,
    dto: AddressUpdateDTO,
    current_user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service)
):
    """Update an address"""
    try:
        existing = await service.get_by_id(address_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Address not found")
        
        # Admin/Secretary can update any
        if current_user.user_type_id in [1, 2]:
            return await service.update_address(address_id, dto)
        
        # Users can only update their own
        if existing.user_id == current_user.id:
            return await service.update_address(address_id, dto)
        
        raise HTTPException(status_code=403, detail="Can only update your own addresses")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{address_id}")
async def delete_address(
    address_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service)
):
    """Delete an address"""
    existing = await service.get_by_id(address_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Admin/Secretary can delete any
    if current_user.user_type_id in [1, 2]:
        deleted = await service.delete(address_id)
        return {"message": "Address deleted successfully"}
    
    # Users can only delete their own
    if existing.user_id == current_user.id:
        deleted = await service.delete(address_id)
        return {"message": "Address deleted successfully"}
    
    raise HTTPException(status_code=403, detail="Can only delete your own addresses")