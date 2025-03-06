from sqlalchemy import Column, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from .base import SQLBaseModel


class UserAddress(SQLBaseModel):
    """SQLAlchemy model for user addresses"""

    __tablename__ = "user_addresses"

    # Address ID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Foreign key to users table
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Address components
    street = Column(String(255), nullable=True)
    house_number = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)

    # Optional label for this address (e.g., "Home", "Work", etc.)
    label = Column(String(50), nullable=True)

    # Whether this is the default address for the user
    is_default = Column(Boolean, default=False)

    # Geographical coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relationship to User
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return (
            f"<UserAddress {self.id}: {self.street} {self.house_number}, {self.city}>"
        )

    @property
    def formatted_address(self) -> str:
        """Generate a formatted address string from components"""
        return f"{self.house_number} {self.street}, {self.city}, {self.postcode}, {self.country}"
