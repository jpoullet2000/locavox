from typing import Dict, Optional, Any
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from .user_address import Coordinates


class Message(BaseModel):
    """Message model representing a user's message in a topic"""

    id: str
    content: str
    user_id: str = Field(default=None, alias="userId")
    address_id: Optional[str] = Field(
        default=None, alias="addressId"
    )  # Reference to a user address
    timestamp: datetime
    coordinates: Optional[Coordinates] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(BaseModel):
    """Model for creating a new message"""

    content: str
    user_id: Optional[str] = Field(default=None, alias="userId")
    address_id: Optional[str] = Field(
        default=None, alias="addressId"
    )  # Reference to a user address
    coordinates: Optional[Coordinates] = None  # Allow direct coordinates input
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        # Allow population by name or alias
        populate_by_name = True
        # Make aliases work when deserializing data from JSON
        populate_by_alias = True
        # Enable aliased field names on models with alias definitions
        allow_population_by_field_name = True

        json_schema_extra = {
            "examples": [
                {
                    "content": "This is a message",
                    "user_id": "user123",  # Snake case version
                    "address_id": "addr456",
                    "metadata": {"key": "value"},
                },
                {
                    "content": "This is a message",
                    "userId": "user123",  # Camel case version
                    "addressId": "addr456",
                    "metadata": {"key": "value"},
                },
            ]
        }


class MessageResponse(BaseModel):
    """Response model for a message"""

    id: str
    content: str
    # Support both snake_case and camelCase field names for user_id
    user_id: Optional[str] = None
    userId: Optional[str] = None
    topic_id: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        # Allow population by name or alias
        populate_by_name = True
        # Enable field validation before model alias validation
        validate_assignment = True

        # Define alias for converting between snake_case and camelCase
        json_schema_extra = {
            "examples": [
                {
                    "id": "123",
                    "content": "This is a message",
                    "user_id": "user123",  # Snake case version
                    "topic_id": "topic456",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "metadata": {"key": "value"},
                }
            ]
        }

    # Change validator to field_validator for Pydantic v2
    @field_validator("userId", mode="before")
    @classmethod
    def sync_user_id(cls, v, info):
        # Get values from the info object in Pydantic v2
        values = info.data
        # If user_id is set and userId is not, use user_id
        if v is None and "user_id" in values and values["user_id"] is not None:
            return values["user_id"]
        return v

    @field_validator("user_id", mode="before")
    @classmethod
    def sync_userId(cls, v, info):
        # Get values from the info object in Pydantic v2
        values = info.data
        # If userId is set and user_id is not, use userId
        if v is None and "userId" in values and values["userId"] is not None:
            return values["userId"]
        return v
