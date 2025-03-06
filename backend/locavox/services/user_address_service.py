from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..models.sql.user import User  # Import User model to check if user exists
from ..models.sql.user_address import UserAddress  # Import the correct SQL model
from ..models.schemas.user_address import (
    UserAddressCreate,
    UserAddressUpdate,
    UserAddressResponse,
)
from ..utils.geocoding import geocode_address

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """Raised when a user_id doesn't exist in the database."""

    pass


async def get_user_addresses(db: AsyncSession, user_id: str) -> List[UserAddress]:
    """
    Get all addresses for a specific user.

    Args:
        db: Database session
        user_id: ID of the user whose addresses to retrieve

    Returns:
        List of UserAddress objects
    """
    try:
        result = await db.execute(
            select(UserAddress).where(UserAddress.user_id == user_id)
        )
        addresses = result.scalars().all()
        logger.info(f"Retrieved {len(addresses)} addresses for user {user_id}")
        return addresses
    except Exception as e:
        logger.error(f"Error getting addresses for user {user_id}: {str(e)}")
        raise


async def create_user_address(
    db: AsyncSession, user_id: str, address: UserAddressCreate
) -> UserAddress:
    """
    Create a new address for a user.

    Args:
        db: Database session
        user_id: ID of the user
        address: Address data

    Returns:
        Created UserAddress object

    Raises:
        UserNotFoundError: If the user doesn't exist
    """
    try:
        # First check if the user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"Cannot create address: User with ID {user_id} not found")
            raise UserNotFoundError(f"User with ID {user_id} doesn't exist")

        # Continue with address creation
        address_dict = address.dict()

        # Geocode the address if coordinates are not provided
        if address.latitude is None or address.longitude is None:
            address_components = {
                "street": address.street,
                "house_number": address.house_number,
                "city": address.city,
                "postcode": address.postcode,
                "country": address.country,
            }

            geocode_result = await geocode_address(address_components)
            if geocode_result.success:
                address_dict["latitude"] = geocode_result.latitude
                address_dict["longitude"] = geocode_result.longitude
                logger.info(
                    f"Successfully geocoded address to {geocode_result.latitude}, {geocode_result.longitude}"
                )
            else:
                logger.warning(f"Failed to geocode address: {geocode_result.message}")

        db_address = UserAddress(**address_dict, user_id=user_id)
        db.add(db_address)

        # If this address is set as default, we need to unset any other default addresses
        if address.is_default:
            await _unset_other_default_addresses(db, user_id, None)

        await db.commit()
        await db.refresh(db_address)
        logger.info(f"Created new address {db_address.id} for user {user_id}")
        return db_address
    except UserNotFoundError:
        # Re-raise this specific error for handling in the API layer
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating address for user {user_id}: {str(e)}")
        raise


async def update_user_address(
    db: AsyncSession, address_id: str, user_id: str, address_update: UserAddressUpdate
) -> Optional[UserAddress]:
    """
    Update an existing address.

    Args:
        db: Database session
        address_id: ID of the address to update
        user_id: ID of the user who owns the address
        address_update: Updated address data

    Returns:
        Updated UserAddress object or None if not found
    """
    try:
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id, UserAddress.user_id == user_id
            )
        )
        db_address = result.scalars().first()

        if not db_address:
            logger.warning(f"Address {address_id} not found for user {user_id}")
            return None

        # Get update data excluding unset fields
        update_data = address_update.dict(exclude_unset=True)

        # Check if we need to geocode the address
        needs_geocoding = False
        address_components = {}

        if any(
            field in update_data
            for field in ["street", "house_number", "city", "postcode", "country"]
        ):
            # We need to build the complete address components dictionary with updated + existing values
            address_components = {
                "street": update_data.get("street", db_address.street),
                "house_number": update_data.get(
                    "house_number", db_address.house_number
                ),
                "city": update_data.get("city", db_address.city),
                "postcode": update_data.get("postcode", db_address.postcode),
                "country": update_data.get("country", db_address.country),
            }
            needs_geocoding = True

        # Geocode if necessary
        if needs_geocoding:
            geocode_result = await geocode_address(address_components)
            if geocode_result.success:
                update_data["latitude"] = geocode_result.latitude
                update_data["longitude"] = geocode_result.longitude
                logger.info(
                    f"Successfully geocoded updated address to {geocode_result.latitude}, {geocode_result.longitude}"
                )
            else:
                logger.warning(
                    f"Failed to geocode updated address: {geocode_result.message}"
                )

        # Update the address fields
        for key, value in update_data.items():
            setattr(db_address, key, value)

        # If this address is set as default, we need to unset any other default addresses
        if update_data.get("is_default", False):
            await _unset_other_default_addresses(db, user_id, address_id)

        await db.commit()
        await db.refresh(db_address)
        logger.info(f"Updated address {address_id} for user {user_id}")
        return db_address
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating address {address_id}: {str(e)}")
        raise


async def delete_user_address(db: AsyncSession, address_id: str, user_id: str) -> bool:
    """
    Delete a user address.

    Args:
        db: Database session
        address_id: ID of the address to delete
        user_id: ID of the user who owns the address

    Returns:
        True if deletion was successful, False if address not found
    """
    try:
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id, UserAddress.user_id == user_id
            )
        )
        db_address = result.scalars().first()

        if not db_address:
            logger.warning(
                f"Address {address_id} not found for user {user_id} during deletion"
            )
            return False

        await db.delete(db_address)
        await db.commit()
        logger.info(f"Deleted address {address_id} for user {user_id}")
        return True
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting address {address_id}: {str(e)}")
        raise


async def _unset_other_default_addresses(
    db: AsyncSession, user_id: str, current_address_id: Optional[str] = None
) -> None:
    """
    Unset the default flag on all other addresses for this user.

    Args:
        db: Database session
        user_id: ID of the user
        current_address_id: ID of the address to exclude (the one being set as default)
    """
    try:
        query = select(UserAddress).where(
            UserAddress.user_id == user_id, UserAddress.is_default == True
        )

        if current_address_id:
            query = query.where(UserAddress.id != current_address_id)

        result = await db.execute(query)
        other_default_addresses = result.scalars().all()

        for addr in other_default_addresses:
            addr.is_default = False

        logger.debug(
            f"Unset default flag on {len(other_default_addresses)} other addresses for user {user_id}"
        )
    except Exception as e:
        logger.error(f"Error unsetting other default addresses: {str(e)}")
        raise
