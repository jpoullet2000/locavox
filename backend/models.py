from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from storage import TopicStorage

class Message(BaseModel):
    # ...existing code...

class BaseTopic:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.storage = TopicStorage(name)
        self.messages: List[Message] = []

    async def add_message(self, message: Message):
        await self.storage.add_message(message.dict())
        self.messages.append(message)

    async def search_messages(self, query: str) -> List[Message]:
        return await self.storage.search_messages(query)

# ...existing code for CommunityTaskMarketplace and NeighborhoodHubChat...
