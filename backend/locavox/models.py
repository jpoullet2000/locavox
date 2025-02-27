from typing import List
from .base_models import Message
from .storage import TopicStorage


class Topic:
    def __init__(self, name: str):
        self.name = name
        self.description = f"Dynamic topic: {name}"
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)


class BaseTopic:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.storage = TopicStorage(name)
        self.messages: List[Message] = []
        self.storage.initialize()  # Initialize storage synchronously

    async def add_message(self, message: Message):
        self.storage.add_message(message.model_dump())  # Remove await
        self.messages.append(message)

    async def search_messages(self, query: str) -> List[Message]:
        return self.storage.search_messages(query)  # Remove await


class CommunityTaskMarketplace(BaseTopic):
    def __init__(self):
        super().__init__(
            "Community Task Marketplace", "Local tasks and services exchange"
        )


class NeighborhoodHubChat(BaseTopic):
    def __init__(self):
        super().__init__("Neighborhood Hub Chat", "General neighborhood discussions")
