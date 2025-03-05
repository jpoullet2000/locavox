from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .base import Base


class User(Base):
    __tablename__ = "users"

    # Make sure id is String type to match with UserAddress.user_id
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add relationship to UserAddress
    addresses = relationship(
        "UserAddress", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


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
