from sqlalchemy import Column, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserAddress(BaseModel):
    """SQLAlchemy model for user addresses"""

    __tablename__ = "user_addresses"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    address = Column(String(255), nullable=False)
    label = Column(String(50), nullable=True)  # e.g., "Home", "Work", etc.
    is_default = Column(Boolean, default=False)

    # Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Relationship
    user = relationship("User", back_populates="addresses")
