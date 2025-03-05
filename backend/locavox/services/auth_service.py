from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from locavox.models.sql.user import User
from locavox.models.schemas.user import TokenData
from locavox.database import get_db_session  # Change to get_db_session
from locavox.utils.security import verify_password
from locavox import config

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate_user(
    db: AsyncSession, email_or_username: str, password: str
) -> Optional[User]:
    """
    Authenticate a user by email/username and password

    Args:
        db: Database session
        email_or_username: Email address or username
        password: Plain text password

    Returns:
        User object if authentication is successful, None otherwise
    """
    # Try to find user by email or username
    stmt = select(User).where(
        (User.email == email_or_username) | (User.username == email_or_username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # If user not found or password doesn't match, return None
    if not user or not verify_password(password, user.hashed_password):
        return None

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        JWT token as string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),  # Change to get_db_session
) -> User:
    """
    Get current user from token

    Args:
        token: JWT token
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate the token
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        token_data = TokenData(sub=user_id)
    except JWTError:
        raise credentials_exception

    # Get the user from the database
    stmt = select(User).where(User.id == token_data.sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),  # Change to get_db_session
) -> Optional[User]:
    """
    Get current user from token, but don't require authentication

    Args:
        token: JWT token (optional)
        db: Database session

    Returns:
        User object or None if no valid token provided
    """
    if token is None:
        return None

    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
