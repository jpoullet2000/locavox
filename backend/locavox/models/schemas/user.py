from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base model for user data"""

    email: EmailStr
    username: str
    name: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user with password"""

    password: str


class UserResponse(UserBase):
    """User response model"""

    id: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Model for updating user data"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data stored in JWT token"""

    sub: Optional[str] = None  # user ID
