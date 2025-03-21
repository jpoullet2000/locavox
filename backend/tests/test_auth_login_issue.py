import asyncio
import logging
import sys
from locavox.services import auth_service
from locavox.database import get_db_session
from locavox.logger import setup_logger

# Set up logging
logger = setup_logger(__name__, level=logging.INFO)


async def verify_user_credentials(username, password):
    """Test function to verify user credentials directly"""
    logger.info(f"Attempting to authenticate user: {username}")

    # Get a database session
    async for db in get_db_session():
        # Try to authenticate the user
        user = await auth_service.authenticate_user(db, username, password)

        if user:
            logger.info(f"Authentication successful for user: {user.username}")
            logger.info(f"User ID: {user.id}")
            logger.info(f"User is_active: {user.is_active}")
            logger.info(f"User is_superuser: {user.is_superuser}")
            return user
        else:
            logger.error(f"Authentication failed for username: {username}")

            # Check if the user exists at all
            from sqlalchemy import select
            from locavox.models.sql.user import User

            # Find by username
            result = await db.execute(select(User).where(User.username == username))
            user_by_username = result.scalar_one_or_none()

            if user_by_username:
                logger.info(f"User with username '{username}' exists in database")
                logger.info(
                    f"Stored password hash: {user_by_username.hashed_password[:10]}..."
                )
                # Check password verification
                from locavox.utils.security import verify_password

                is_valid = verify_password(password, user_by_username.hashed_password)
                logger.info(f"Password verification result: {is_valid}")
                return None
            else:
                logger.error(f"No user found with username: {username}")

                # Try looking up by email
                result = await db.execute(select(User).where(User.email == username))
                user_by_email = result.scalar_one_or_none()

                if user_by_email:
                    logger.info(f"User with email '{username}' exists in database")
                    logger.info(f"Username is actually: {user_by_email.username}")
                    return None
                else:
                    logger.error(f"No user found with email: {username}")
                    return None


async def main():
    """Main function to run the test"""
    if len(sys.argv) < 3:
        print("Usage: python -m tests.test_auth_login_issue <username> <password>")
        return

    username = sys.argv[1]
    password = sys.argv[2]

    user = await verify_user_credentials(username, password)

    if user:
        print(f"✅ Authentication successful for user: {user.username}")
    else:
        print(f"❌ Authentication failed for username: {username}")

        # Provide some common troubleshooting tips
        print("\nTroubleshooting tips:")
        print("1. Check if you're using the correct username (not email)")
        print("2. Verify your password is correct")
        print("3. Make sure the user is active in the database")
        print("4. Check if you're connecting to the correct database")
        print("5. Inspect database values directly with an SQLite browser")


if __name__ == "__main__":
    asyncio.run(main())
