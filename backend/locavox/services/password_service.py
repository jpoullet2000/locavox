import bcrypt
import logging

logger = logging.getLogger(__name__)


class PasswordService:
    """
    Service for handling password hashing and verification without relying on passlib.
    This avoids the bcrypt.__about__ issue.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password as string
        """
        if isinstance(password, str):
            password = password.encode("utf-8")

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches hash, False otherwise
        """
        try:
            if isinstance(plain_password, str):
                plain_password = plain_password.encode("utf-8")

            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode("utf-8")

            return bcrypt.checkpw(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False


# Create a singleton instance
password_service = PasswordService()
