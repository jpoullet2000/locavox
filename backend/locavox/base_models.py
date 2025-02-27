from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel


class Message(BaseModel):
    id: str
    content: str
    userId: str
    timestamp: datetime
    metadata: Optional[Dict] = None
