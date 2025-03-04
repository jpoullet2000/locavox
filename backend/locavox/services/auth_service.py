from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta, timezone
from ..models.user import User, UserCreate
from .. import config  # Import the config module directly
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Try to import 'jose', provide helpful error if not available
try:
    from jose import JWTError, jwt
except ImportError:
    jwt = None
    JWTError = Exception
    logger.error(
        "Missing dependency: 'python-jose' not found. Please install it using: "
        "pip install 'python-jose[cryptography]'"
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validate the token and return the current user.
    Raises exception if token is invalid or missing.
    """
    if jwt is None:
        logger.error(
            "JWT functionality is disabled because 'python-jose' is not installed"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT authentication is not available. Please contact the administrator.",
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        # Decode the JWT token using config variables directly
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Get the user from the database
        breakpoint()
        user = await get_user_by_id(user_id)

        if user is None:
            raise credentials_exception

        return user
    except JWTError:
        raise credentials_exception


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Validate the token and return the current user, or None if no token provided.
    Does not raise exception if token is missing, but still validates if provided.
    """
    if token is None:
        return None

    try:
        if jwt is None:
            logger.warning(
                "JWT functionality is disabled because 'python-jose' is not installed"
            )
            return None

        # Decode the JWT token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        # Get the user from the database
        user = await get_user_by_id(user_id)
        return user
    except JWTError:
        return None


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password
    For now, returns a dummy user if username matches password
    """
    if not username or not password:
        return None
    breakpoint()
    if username == "admin" and password == "admin":
        return User(
            id="admin",
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            is_active=True,
            is_admin=True,
        )

    if username == password:  # Simple test authentication
        return User(
            id=f"user-{username}",
            username=username,
            email=f"{username}@example.com",
            is_active=True,
        )
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token with the given data and expiration
    """
    if jwt is None:
        logger.error(
            "JWT functionality is disabled because 'python-jose' is not installed"
        )
        return "dummy-token"  # Return a dummy token if jose is not installed

    to_encode = data.copy()

    # Use timezone-aware datetime objects (recommended approach)
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire.timestamp()})

    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def register_user(user_data: UserCreate) -> User:
    """
    Register a new user
    For now, returns a dummy user with the provided data
    """
    # In a real app, you would:
    # 1. Check if the username/email is already taken
    # 2. Hash the password
    # 3. Store the user in the database
    # 4. Return the created user

    new_user = User(
        id=f"user-{user_data.username}",
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True,
    )
    return new_user


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user from the database by ID
    For now, returns a dummy user if the ID starts with 'user-'
    """
    if user_id.startswith("user-"):
        username = user_id[5:]
        if username == "admin":
            return User(
                id="admin",
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                is_active=True,
                is_admin=True,
            )
        return User(
            id=user_id,
            username=username,
            email=f"{username}@example.com",
            is_active=True,
        )
    return None
