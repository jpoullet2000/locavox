import asyncio
import argparse
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import sys
import os

# Add parent directory to path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from locavox import config
from locavox.models import Base
from locavox.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_table_exists(table_name):
    """Check if a table exists in the database"""
    async with engine.connect() as conn:
        if engine.dialect.name == "postgresql":
            result = await conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                )
                """),
                {"table_name": table_name},
            )
        elif engine.dialect.name == "sqlite":
            result = await conn.execute(
                text("""
                SELECT count(name) FROM sqlite_master 
                WHERE type='table' AND name=:table_name
                """),
                {"table_name": table_name},
            )
        else:
            raise NotImplementedError(
                f"Database dialect {engine.dialect.name} not supported"
            )

        return await result.scalar()


async def fix_user_address_foreign_key():
    """Fix the data type mismatch between User.id and UserAddress.user_id"""
    async with engine.begin() as conn:
        # Check if the tables exist
        users_exist = await check_table_exists("users")
        addresses_exist = await check_table_exists("user_addresses")

        if not users_exist or not addresses_exist:
            logger.info("Tables don't exist yet. No migration needed.")
            return

        logger.info("Backing up data...")
        # Create temporary tables to store data
        if engine.dialect.name == "postgresql":
            await conn.execute(
                text("CREATE TEMP TABLE tmp_users AS SELECT * FROM users")
            )
            await conn.execute(
                text("CREATE TEMP TABLE tmp_addresses AS SELECT * FROM user_addresses")
            )
        else:
            await conn.execute(
                text("CREATE TEMPORARY TABLE tmp_users AS SELECT * FROM users")
            )
            await conn.execute(
                text(
                    "CREATE TEMPORARY TABLE tmp_addresses AS SELECT * FROM user_addresses"
                )
            )

        # Drop existing tables
        logger.info("Dropping tables...")
        await conn.run_sync(Base.metadata.drop_all)

        # Recreate tables with correct schema
        logger.info("Recreating tables with correct schema...")
        await conn.run_sync(Base.metadata.create_all)

        # Restore data
        logger.info("Restoring data...")
        # Note: This assumes both tables use string IDs
        await conn.execute(text("INSERT INTO users SELECT * FROM tmp_users"))
        await conn.execute(
            text("INSERT INTO user_addresses SELECT * FROM tmp_addresses")
        )

        logger.info("Migration completed successfully")


async def main():
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--fix-user-address-fk",
        action="store_true",
        help="Fix user_address foreign key data type mismatch",
    )
    args = parser.parse_args()

    if args.fix_user_address_fk:
        await fix_user_address_foreign_key()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
