from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from locavox.models.sql.user import User  # Import SQLAlchemy model
from locavox.models.schemas.user import UserCreate  # Import Pydantic schema
from locavox.utils.security import get_password_hash
from locavox.logger import setup_logger

logger = setup_logger(__name__)


class UserExistsError(Exception):
    """Raised when attempting to create a user with an email that already exists."""

    pass


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user in the database

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        The created user object

    Raises:
        UserExistsError: If a user with the same email already exists
    """
    try:
        # Check if user with this email already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise UserExistsError(f"User with email {user_data.email} already exists")

        # Create new user
        hashed_password = get_password_hash(user_data.password)

        user_dict = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_active": True,
        }

        # Add optional fields only if they exist in the model and are provided
        if hasattr(user_data, "username") and user_data.username:
            user_dict["username"] = user_data.username

        if hasattr(user_data, "name") and user_data.name:
            user_dict["name"] = user_data.name

        if hasattr(user_data, "full_name") and user_data.full_name:
            user_dict["full_name"] = user_data.full_name

        user = User(**user_dict)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Created user with email: {user.email}, id: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        await db.rollback()
        raise
