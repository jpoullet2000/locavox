from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Coordinates(BaseModel):
    """Model representing geographical coordinates"""

    latitude: float
    longitude: float


class UserAddressBase(BaseModel):
    """Base model for user address data"""

    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
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


class UserAddressResponse(UserAddressBase):
    """User address response model"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Create coordinates property for compatibility with existing code
    @property
    def coordinates(self) -> Optional[Coordinates]:
        if self.latitude is not None and self.longitude is not None:
            return Coordinates(latitude=self.latitude, longitude=self.longitude)
        return None

    class Config:
        from_attributes = True
