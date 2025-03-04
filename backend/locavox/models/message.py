from typing import Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    """Message model representing a user's message in a topic"""

    id: str
    content: str
    userId: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(BaseModel):
    """Model for creating a new message"""

    content: str
    userId: str
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Model for API response containing a message"""

    id: str
    content: str
    userId: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
