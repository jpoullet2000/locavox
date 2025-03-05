from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class User(BaseModel):
    """SQLAlchemy model for users"""

    __tablename__ = "users"

    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100), nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255))
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships
    addresses = relationship(
        "UserAddress", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"
