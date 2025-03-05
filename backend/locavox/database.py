import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging
import os

from . import config

# Set up logging
try:
    from .logger import setup_logger

    logger = setup_logger(__name__)
except (ImportError, AttributeError):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

# Get database URL from environment or use SQLite in-memory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./locavox.db")

# Check if we're using PostgreSQL and handle missing dependencies
if DATABASE_URL and DATABASE_URL.startswith("postgresql+asyncpg"):
    try:
        import asyncpg
    except ImportError:
        logger.error(
            "The asyncpg package is required for PostgreSQL connections. "
            "Please install it with: pip install asyncpg"
        )
        # Fall back to SQLite for development if PostgreSQL is unavailable
        if config.settings.ENVIRONMENT == "development":
            logger.warning("Falling back to SQLite for development")
            DATABASE_URL = "sqlite+aiosqlite:///./locavox_dev.db"
            try:
                import aiosqlite
            except ImportError:
                logger.error(
                    "aiosqlite package is also missing. Please install required packages: pip install asyncpg aiosqlite"
                )
                sys.exit(1)
        else:
            logger.critical(
                "Cannot connect to PostgreSQL database without asyncpg package"
            )
            sys.exit(1)

# Create async engine with appropriate URL
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        future=True,
    )

    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info(f"Database engine created with {DATABASE_URL.split('://', 1)[0]}")
except Exception as e:
    logger.critical(f"Failed to create database engine: {str(e)}")
    sys.exit(1)


# Dependency to get database session
@asynccontextmanager
async def get_db():
    """Async context manager to handle database session lifecycle"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise


# For compatibility with FastAPI dependency injection
async def get_db_session():
    """
    Dependency that yields a database session for FastAPI routes.
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# This function will be called to initialize tables
async def init_db():
    """Initialize the database tables"""
    # Import all models to ensure they're registered with SQLAlchemy
    from .models import Base  # This now imports the Base and all models

    try:
        async with engine.begin() as conn:
            # When testing, we might want to recreate tables
            if config.settings.TESTING and config.settings.DATABASE_RECREATE_TABLES:
                logger.warning(
                    "Dropping all tables as TESTING and DATABASE_RECREATE_TABLES are set"
                )
                await conn.run_sync(Base.metadata.drop_all)

            # Check if tables exist before creating
            inspector = await conn.run_sync(
                lambda sync_conn: engine.dialect.has_table(sync_conn, "users")
            )

            if not inspector:
                # Create tables if they don't exist
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
            else:
                logger.info("Database tables already exist")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {str(e)}")
        raise
