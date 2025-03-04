from pydantic import BaseModel, Field
from typing import Optional, List
import datetime
import uuid


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
