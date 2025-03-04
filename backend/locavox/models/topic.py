from pydantic import BaseModel, Field
from typing import Optional, List
import datetime
import uuid
from .message import Message
from ..logger import setup_logger

logger = setup_logger(__name__)


class TopicBase(BaseModel):
    """Base model for Topic"""

    title: str
    description: str
    category: Optional[str] = None
    image_url: Optional[str] = None


class TopicCreate(TopicBase):
    """Model for creating a new topic"""

    pass


class TopicUpdate(BaseModel):
    """Model for updating an existing topic"""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class Topic(TopicBase):
    """Complete Topic model including database fields"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        orm_mode = True


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
