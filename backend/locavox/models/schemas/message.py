from typing import Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime
from .user_address import Coordinates


class Message(BaseModel):
    """Message model representing a user's message in a topic"""

    id: str
    content: str
    userId: str
    timestamp: datetime
    coordinates: Optional[Coordinates] = None
    addressId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(BaseModel):
    """Model for creating a new message"""

    content: str
    userId: str
    addressId: Optional[str] = None  # Reference to a user address
    coordinates: Optional[Coordinates] = None  # Allow direct coordinates input
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Model for API response containing a message"""

    id: str
    content: str
    userId: str
    timestamp: datetime
    coordinates: Optional[Coordinates] = None
    addressId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
