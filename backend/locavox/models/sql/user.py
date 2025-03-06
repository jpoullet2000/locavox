from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from .base import SQLBaseModel


class User(SQLBaseModel):
    """SQLAlchemy model for users"""

    __tablename__ = "users"

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
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
