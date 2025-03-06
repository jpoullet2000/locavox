import asyncio
import sys
import os

# Add parent directory to path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from locavox.database import engine
from locavox import config
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_missing_columns():
    """Add missing columns to the user_addresses table"""
    logger.info(
        "Starting database migration - adding missing columns to user_addresses table..."
    )

    async with engine.begin() as conn:
        try:
            # Check if the table exists first
            if engine.dialect.name == "sqlite":
                table_exists = await conn.execute(
                    text(
                        "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='user_addresses'"
                    )
                )
                exists = await table_exists.scalar()

                if not exists:
                    logger.info("Table 'user_addresses' doesn't exist, creating it...")
                    # Import models to ensure they're registered
                    from locavox.models import Base
                    from locavox.models.sql.user_address import UserAddress

                    # Create the table
                    await conn.run_sync(
                        lambda sync_conn: Base.metadata.create_all(
                            bind=sync_conn, tables=[UserAddress.__table__]
                        )
                    )
                    logger.info("Table 'user_addresses' created successfully")
                    return

                # Check existing columns
                result = await conn.execute(text("PRAGMA table_info(user_addresses)"))
                columns = result.fetchall()
                existing_columns = [column[1] for column in columns]

                logger.info(f"Existing columns: {existing_columns}")

                # Add missing columns
                required_columns = [
                    "street",
                    "house_number",
                    "city",
                    "postcode",
                    "country",
                    "label",
                    "is_default",
                    "latitude",
                    "longitude",
                ]

                for column in required_columns:
                    if column not in existing_columns:
                        logger.info(f"Adding '{column}' column to user_addresses table")
                        column_type = (
                            "FLOAT"
                            if column in ["latitude", "longitude"]
                            else "BOOLEAN"
                            if column == "is_default"
                            else "VARCHAR"
                        )
                        await conn.execute(
                            text(
                                f"ALTER TABLE user_addresses ADD COLUMN {column} {column_type}"
                            )
                        )

            elif engine.dialect.name == "postgresql":
                # PostgreSQL version - check if table exists
                table_exists = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'user_addresses'
                        )
                        """
                    )
                )
                exists = await table_exists.scalar()

                if not exists:
                    logger.info("Table 'user_addresses' doesn't exist, creating it...")
                    # Import models to ensure they're registered
                    from locavox.models import Base
                    from locavox.models.sql.user_address import UserAddress

                    # Create the table
                    await conn.run_sync(
                        lambda sync_conn: Base.metadata.create_all(
                            bind=sync_conn, tables=[UserAddress.__table__]
                        )
                    )
                    logger.info("Table 'user_addresses' created successfully")
                    return

                # PostgreSQL version - can add all columns in a single DO block
                await conn.execute(
                    text("""
                    DO $$
                    BEGIN
                        -- Check and add street column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'street'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN street VARCHAR(255);
                        END IF;
                        
                        -- Check and add house_number column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'house_number'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN house_number VARCHAR(20);
                        END IF;
                        
                        -- Check and add city column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'city'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN city VARCHAR(100);
                        END IF;
                        
                        -- Check and add postcode column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'postcode'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN postcode VARCHAR(20);
                        END IF;
                        
                        -- Check and add country column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'country'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN country VARCHAR(100);
                        END IF;
                        
                        -- Check and add label column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'label'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN label VARCHAR(50);
                        END IF;
                        
                        -- Check and add is_default column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'is_default'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN is_default BOOLEAN DEFAULT FALSE;
                        END IF;
                        
                        -- Check and add latitude column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'latitude'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN latitude FLOAT;
                        END IF;
                        
                        -- Check and add longitude column
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'user_addresses' AND column_name = 'longitude'
                        ) THEN
                            ALTER TABLE user_addresses ADD COLUMN longitude FLOAT;
                        END IF;
                    END;
                    $$;
                """)
                )
            else:
                logger.error(f"Unsupported database dialect: {engine.dialect.name}")
                return

            logger.info("Migration completed successfully")

        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            raise


async def main():
    await add_missing_columns()


if __name__ == "__main__":
    asyncio.run(main())
