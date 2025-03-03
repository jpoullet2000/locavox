from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    """Base model for user data"""

    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user with password"""

    password: str


class User(UserBase):
    """User model for API responses and internal use"""

    id: str
    is_active: bool = True
    is_admin: bool = False

    class Config:
        from_attributes = True  # For ORM compatibility


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data stored in JWT token"""

    sub: Optional[str] = None  # user ID
