#!/usr/bin/env python3
"""
Tool to create an admin user for the Locavox application.
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add the parent directory to sys.path to import modules from the main application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from locavox.database import get_db_session, init_db
from locavox.services.user_service import create_user
from locavox.models.schemas.user import UserCreate
from locavox.logger import setup_logger

logger = setup_logger(__name__)


async def create_admin_user(
    username: str, email: str, password: str, force: bool = False
):
    """Create a new admin user."""
    try:
        # Initialize the database
        await init_db()

        # Create a session
        async for session in get_db_session():
            # Check if user already exists
            from sqlalchemy import select
            from locavox.models.sql.user import User

            query = select(User).where(
                (User.username == username) | (User.email == email)
            )
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user and not force:
                if existing_user.username == username:
                    logger.error(f"User with username '{username}' already exists.")
                else:
                    logger.error(f"User with email '{email}' already exists.")
                return False

            # Create the user with superuser privileges
            user_data = UserCreate(
                username=username,
                email=email,
                password=password,
            )

            # Create the user first - pass session to create_user
            new_user = await create_user(user_data=user_data, db=session)

            # Then update the user to make them a superuser
            if new_user:
                # Update the user directly in the database to make them a superuser
                new_user.is_superuser = True
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                logger.info(
                    f"Admin user '{username}' created successfully with ID: {new_user.id}"
                )
                return True
            else:
                logger.error("Failed to create admin user")
                return False

    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create an admin user for Locavox")
    parser.add_argument("--username", "-u", required=True, help="Admin username")
    parser.add_argument("--email", "-e", required=True, help="Admin email")
    parser.add_argument("--password", "-p", required=True, help="Admin password")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Force create even if user exists"
    )

    args = parser.parse_args()

    success = asyncio.run(
        create_admin_user(
            username=args.username,
            email=args.email,
            password=args.password,
            force=args.force,
        )
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
