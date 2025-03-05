from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas.user_address import (
    UserAddressCreate,
    UserAddressResponse,
    UserAddressUpdate,
)
from ..services.user_address_service import (
    get_user_addresses,
    create_user_address,
    update_user_address,
    delete_user_address,
)
from ..dependencies import get_db  # Updated import from dependencies module
from ..logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["user-addresses"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{user_id}/addresses", response_model=List[UserAddressResponse])
async def get_addresses(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all addresses for a user"""
    addresses = await get_user_addresses(db, user_id)
    return addresses


@router.post(
    "/{user_id}/addresses",
    response_model=UserAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_user_address(
    user_id: str, address: UserAddressCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new address for a user"""
    db_address = await create_user_address(db, user_id, address)
    return db_address


@router.put("/{user_id}/addresses/{address_id}", response_model=UserAddressResponse)
async def edit_user_address(
    user_id: str,
    address_id: str,
    address_update: UserAddressUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing address"""
    db_address = await update_user_address(db, address_id, user_id, address_update)
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return db_address


@router.delete(
    "/{user_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_user_address(
    user_id: str, address_id: str, db: AsyncSession = Depends(get_db)
):
    """Delete a user address"""
    success = await delete_user_address(db, address_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return None
