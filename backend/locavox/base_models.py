from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str
    content: str
    userId: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
