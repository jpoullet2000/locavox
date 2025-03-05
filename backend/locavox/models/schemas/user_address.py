from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from .base import Base  # Import Base from base.py instead of creating a new one


class Coordinates(BaseModel):
    """Model representing geographical coordinates"""

    latitude: float
    longitude: float


class UserAddressBase(BaseModel):
    """Base model for user addresses"""

    street: str
    house_number: str
    city: str
    postcode: str
    country: str
    label: Optional[str] = None
    is_default: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserAddressCreate(UserAddressBase):
    """Model for creating a new user address"""

    pass


class UserAddressUpdate(BaseModel):
    """Model for updating a user address"""

    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    label: Optional[str] = None
    is_default: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserAddress(Base):
    """SQLAlchemy model for user addresses in the database"""

    __tablename__ = "user_addresses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    street = Column(String, nullable=False)
    house_number = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postcode = Column(String, nullable=False)
    country = Column(String, nullable=False)
    label = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Add relationship to User model
    user = relationship("User", back_populates="addresses")

    @property
    def formatted_address(self) -> str:
        """Generate a formatted address string from components"""
        return f"{self.house_number} {self.street}, {self.city}, {self.postcode}, {self.country}"


class UserAddressResponse(UserAddressBase):
    """Model for API response containing a user address"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    formatted_address: str

    # Create coordinates property for compatibility with existing code
    @property
    def coordinates(self) -> Optional[Coordinates]:
        if self.latitude is not None and self.longitude is not None:
            return Coordinates(latitude=self.latitude, longitude=self.longitude)
        return None

    class Config:
        from_attributes = True
