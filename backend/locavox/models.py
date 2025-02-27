from typing import List
from .base_models import Message
from .storage import TopicStorage


class Topic:
    def __init__(self, name: str):
        self.name = name
        self.description = f"Dynamic topic: {name}"
        self.messages = []
        self.storage = TopicStorage(name)
        self.storage.initialize()

    async def add_message(self, message: Message):
        self.storage.add_message(message.model_dump())
        self.messages.append(message)
        return message

    async def get_messages(self, limit: int = 100) -> List[Message]:
        return self.storage.get_messages(limit)


class BaseTopic:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.storage = TopicStorage(name)
        self.messages: List[Message] = []

    async def initialize(self):
        await self.storage.initialize()

    def initialize_sync(self):
        """Synchronous initialization"""
        self.storage.initialize_sync()
        return self

    async def add_message(self, message: Message):
        if not self.storage.table:
            await self.storage.initialize()
        await self.storage.add_message(message)
        self.messages.append(message)

    async def search_messages(self, query: str) -> List[Message]:
        if not self.storage.table:
            await self.storage.initialize()
        return await self.storage.search_messages(query)

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get all messages from this topic, newest first."""
        if not self.storage.table:
            await self.storage.initialize()
        return await self.storage.get_messages(limit)


class CommunityTaskMarketplace(BaseTopic):
    def __init__(self):
        super().__init__(
            "Community Task Marketplace", "Local tasks and services exchange"
        )


class NeighborhoodHubChat(BaseTopic):
    def __init__(self):
        super().__init__("Neighborhood Hub Chat", "General neighborhood discussions")
