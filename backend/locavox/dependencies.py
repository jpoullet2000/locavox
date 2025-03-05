from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .logger import setup_logger

logger = setup_logger(__name__)


# Re-export the get_db dependency for convenience
# This allows other modules to import get_db from dependencies
# instead of directly from database
async def get_db_session():
    """
    Dependency that yields a database session and handles commits/rollbacks.
    This is the main database dependency to use in routes.
    """
    async with get_db() as session:
        yield session


# For compatibility with existing code that expects get_db
get_db = get_db_session
