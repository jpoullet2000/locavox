"""
Base models for Locavox backend.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from datetime import datetime
import logging
from ..logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)


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


class BaseTopic:
    """Base class for all topic implementations"""

    def __init__(self, name: str = None, description: str = None):
        self.name = name or "general"
        self.description = description or f"Topic for {self.name}"
        self._messages = []  # Simple in-memory storage

    async def add_message(self, message: Message) -> None:
        """Add a message to this topic"""
        self._messages.append(message)
        logger.info(f"Added message {message.id} to topic {self.name}")

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get recent messages from this topic"""
        # Return the most recent messages first
        sorted_messages = sorted(
            self._messages, key=lambda m: m.timestamp, reverse=True
        )
        return sorted_messages[:limit]

    async def get_messages_by_user(
        self, user_id: str, limit: int = 100
    ) -> List[Message]:
        """Get messages from a specific user in this topic"""
        user_messages = [msg for msg in self._messages if msg.userId == user_id]
        sorted_messages = sorted(user_messages, key=lambda m: m.timestamp, reverse=True)
        return sorted_messages[:limit]

    async def search_messages(self, query: str) -> List[Message]:
        """Search for messages containing the query string"""
        # Simple case-insensitive search
        query_lower = query.lower()
        return [msg for msg in self._messages if query_lower in msg.content.lower()]


class CommunityTaskMarketplace(BaseTopic):
    """Topic for community task marketplace"""

    def __init__(self):
        super().__init__("marketplace", "Community Task Marketplace")

    # Additional specialized methods could be added here


class NeighborhoodHubChat(BaseTopic):
    """Topic for neighborhood hub chat"""

    def __init__(self):
        super().__init__("chat", "Neighborhood Hub Chat")

    # Additional specialized methods could be added here
