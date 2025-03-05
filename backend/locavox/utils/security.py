import bcrypt  # Import bcrypt directly

# Service for password handling
from locavox.services.password_service import password_service


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_service.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return password_service.hash_password(password)


# Alternative direct bcrypt implementation as fallbacks
def get_password_hash_direct(password: str) -> str:
    """
    Generate a password hash using bcrypt directly.
    This is a fallback in case the password service has issues.
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode("utf-8")


def verify_password_direct(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using bcrypt directly.
    This is a fallback in case the password service has issues.
    """
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password, hashed_password)
