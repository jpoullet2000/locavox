import asyncio
import argparse
import logging
import sys
import json

try:
    from .logger import setup_logger

    logger = setup_logger(__name__)
except (ImportError, AttributeError):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


async def init_db_command():
    """Initialize the database tables"""
    from .database import init_db

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully!")


async def list_models_command():
    """List all registered SQLAlchemy models"""
    from .models import Base

    logger.info("Registered SQLAlchemy models:")
    for class_name, table in Base.metadata.tables.items():
        logger.info(f"  • {class_name}")
        for column in table.columns:
            logger.info(
                f"    - {column.name}: {column.type} (PK={column.primary_key}, FK={bool(column.foreign_keys)})"
            )


def show_config_command():
    """Display the current configuration settings"""
    from .config import settings

    logger.info("Current configuration settings:")
    # Convert settings to a dict for easier printing
    config_dict = {
        k: v
        for k, v in settings.__dict__.items()
        if not k.startswith("_") and not callable(v)
    }

    # Handle non-serializable types
    for k, v in config_dict.items():
        if not isinstance(v, (str, int, float, bool, type(None), list, dict)):
            config_dict[k] = str(v)

    # Print configuration settings
    for key, value in sorted(config_dict.items()):
        if key == "SECRET_KEY" and value:
            # Mask sensitive information
            logger.info(f"  {key}: ***MASKED***")
        elif key == "OPENAI_API_KEY" and value:
            # Mask sensitive information
            logger.info(f"  {key}: ***MASKED***")
        else:
            logger.info(f"  {key}: {value}")


async def reset_db_command():
    """Drop all tables and recreate them - Use with caution!"""
    from .models import Base
    from .database import engine

    logger.warning("This will delete all data in the database. Are you sure? (y/n)")
    confirm = input().lower()
    if confirm != "y":
        logger.info("Operation cancelled.")
        return

    logger.info("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("Recreating tables...")
    await init_db_command()


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Locavox CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init DB command
    subparsers.add_parser("init-db", help="Initialize the database")

    # Reset DB command
    subparsers.add_parser(
        "reset-db",
        help="Drop all tables and recreate them (CAUTION: Destroys all data)",
    )

    # List models command
    subparsers.add_parser("list-models", help="List all registered SQLAlchemy models")

    # Show configuration command
    subparsers.add_parser("show-config", help="Display current configuration settings")

    # Parse args
    args = parser.parse_args()

    if args.command == "init-db":
        asyncio.run(init_db_command())
    elif args.command == "reset-db":
        asyncio.run(reset_db_command())
    elif args.command == "list-models":
        asyncio.run(list_models_command())
    elif args.command == "show-config":
        show_config_command()
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        logger.error(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
