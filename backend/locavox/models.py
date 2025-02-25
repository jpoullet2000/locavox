from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    id: str
    content: str
    userId: str
    timestamp: datetime
    metadata: Optional[Dict] = None


class BaseTopic:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.messages: List[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)


class CommunityTaskMarketplace(BaseTopic):
    def __init__(self):
        super().__init__(
            "Community Task Marketplace",
            "A place to share and request community resources and help",
        )


class NeighborhoodHubChat(BaseTopic):
    def __init__(self):
        super().__init__(
            "Neighborhood Hub Chat",
            "General neighborhood discussion and casual conversations",
        )
