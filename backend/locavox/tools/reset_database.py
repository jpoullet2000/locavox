import asyncio
import sys
import os
import logging

# Add parent directory to path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from locavox.database import engine
from locavox.models.sql.base import Base
from locavox import config

# Make sure we're not in production!
if config.settings.ENVIRONMENT == "production":
    print("WARNING: This script should not be run in production!")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reset_database():
    """Drop and recreate all tables"""
    logger.warning("This will delete all data in the database!")
    confirmation = input("Are you sure you want to continue? (y/n): ")

    if confirmation.lower() != "y":
        logger.info("Operation cancelled")
        return

    logger.info("Resetting database...")

    # Import all models to ensure they're registered with SQLAlchemy
    from locavox.models import User, UserAddress

    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Tables dropped")

        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created")

    logger.info("Database reset completed successfully")


if __name__ == "__main__":
    asyncio.run(reset_database())
