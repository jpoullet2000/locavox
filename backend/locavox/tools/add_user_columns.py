import asyncio
import sys
import os

# Add parent directory to path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from locavox.database import engine, init_db
from locavox import config
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_missing_columns():
    """Add missing columns to the users table"""
    logger.info(
        "Starting database migration - adding missing columns to users table..."
    )

    async with engine.begin() as conn:
        try:
            # Check if the name column exists
            if engine.dialect.name == "sqlite":
                result = await conn.execute(text("PRAGMA table_info(users)"))
                columns = result.fetchall()
                existing_columns = [column[1] for column in columns]

                logger.info(f"Existing columns: {existing_columns}")

                # Add name column if it doesn't exist
                if "name" not in existing_columns:
                    logger.info("Adding 'name' column to users table")
                    await conn.execute(
                        text("ALTER TABLE users ADD COLUMN name VARCHAR")
                    )

                # Add full_name column if it doesn't exist
                if "full_name" not in existing_columns:
                    logger.info("Adding 'full_name' column to users table")
                    await conn.execute(
                        text("ALTER TABLE users ADD COLUMN full_name VARCHAR")
                    )

                # Add bio column if it doesn't exist
                if "bio" not in existing_columns:
                    logger.info("Adding 'bio' column to users table")
                    await conn.execute(text("ALTER TABLE users ADD COLUMN bio TEXT"))

                # Add profile_image_url column if it doesn't exist
                if "profile_image_url" not in existing_columns:
                    logger.info("Adding 'profile_image_url' column to users table")
                    await conn.execute(
                        text(
                            "ALTER TABLE users ADD COLUMN profile_image_url VARCHAR(255)"
                        )
                    )

            elif engine.dialect.name == "postgresql":
                # PostgreSQL version - can use a more efficient approach
                # Check and add name column
                await conn.execute(
                    text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'name'
                        ) THEN
                            ALTER TABLE users ADD COLUMN name VARCHAR;
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'full_name'
                        ) THEN
                            ALTER TABLE users ADD COLUMN full_name VARCHAR;
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'bio'
                        ) THEN
                            ALTER TABLE users ADD COLUMN bio TEXT;
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'profile_image_url'
                        ) THEN
                            ALTER TABLE users ADD COLUMN profile_image_url VARCHAR(255);
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
