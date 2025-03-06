from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..models.sql.user import User as UserModel
from ..models.schemas.user_address import (
    UserAddressCreate,
    UserAddressUpdate,
    UserAddressResponse,
)
from ..services.user_address_service import (
    get_user_addresses,
    create_user_address,
    update_user_address,
    delete_user_address,
    UserNotFoundError,
)
from ..services.auth_service import get_current_user
from ..logger import setup_logger
from locavox.database import get_db_session

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["addresses"],
)


@router.get("/{user_id}/addresses", response_model=List[UserAddressResponse])
async def get_addresses_for_user(
    user_id: str = Path(..., title="The ID of the user to get addresses for"),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get all addresses for a specific user.

    This endpoint requires authentication.
    Users can only see their own addresses unless they are admin users.
    """
    # Check if requesting own addresses or has admin rights
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access other users' addresses",
        )

    addresses = await get_user_addresses(db, user_id)
    return addresses


@router.post(
    "/{user_id}/addresses",
    response_model=UserAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_address_for_user(
    address: UserAddressCreate,
    user_id: str = Path(..., title="The ID of the user to create an address for"),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create a new address for a user.

    This endpoint requires authentication.
    Users can only create addresses for themselves unless they are admin users.
    """
    # Check if creating for own account or has admin rights
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create addresses for other users",
        )

    try:
        new_address = await create_user_address(db, user_id, address)
        return new_address
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{user_id}/addresses/{address_id}", response_model=UserAddressResponse)
async def update_address(
    address_update: UserAddressUpdate,
    user_id: str = Path(..., title="The ID of the user who owns the address"),
    address_id: str = Path(..., title="The ID of the address to update"),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update an existing address.

    This endpoint requires authentication.
    Users can only update their own addresses unless they are admin users.
    """
    # Check if updating own address or has admin rights
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update other users' addresses",
        )

    updated_address = await update_user_address(db, address_id, user_id, address_update)
    if not updated_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found for user {user_id}",
        )

    return updated_address


@router.delete(
    "/{user_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_address(
    user_id: str = Path(..., title="The ID of the user who owns the address"),
    address_id: str = Path(..., title="The ID of the address to delete"),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete an address.

    This endpoint requires authentication.
    Users can only delete their own addresses unless they are admin users.
    """
    # Check if deleting own address or has admin rights
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete other users' addresses",
        )

    success = await delete_user_address(db, address_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found for user {user_id}",
        )
