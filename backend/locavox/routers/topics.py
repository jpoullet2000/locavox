from fastapi import APIRouter, Depends, HTTPException, Path, status, Query
from typing import List, Optional, Dict
from ..models.base_models import Message, BaseTopic  # Updated import
from ..services import message_service, auth_service
from ..models.user import User
from ..logger import setup_logger
from pydantic import BaseModel
import uuid
from datetime import datetime
from ..config_helpers import get_message_limit
from ..models import (
    CommunityTaskMarketplace,
    NeighborhoodHubChat,
)  # Import from models/__init__.py

# Set up logger for this module
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
    responses={404: {"description": "Not found"}},
)

# Get references to topics from a central store
from ..topic_registry import get_topics

topics = get_topics()


class MessageRequest(BaseModel):
    userId: str
    content: str
    metadata: Optional[dict] = None


@router.get("")
async def list_topics():
    """List all available topics"""
    if topics is None:
        return {"topics": []}
    return {"topics": list(topics.keys())}


@router.get("/{topic_name}/messages")
async def list_messages(topic_name: str):
    """Get all messages in a topic"""
    if topic_name not in topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    messages = await topics[topic_name].get_messages(10)
    return {"messages": [msg.model_dump() for msg in messages]}


@router.post("/{topic_name}/messages")
async def add_message(
    topic_name: str,
    request: MessageRequest,
    test_limit: Optional[int] = Query(
        None, description="Override message limit for testing"
    ),
    current_user: Optional[User] = Depends(auth_service.get_current_user_optional),
):
    """Add a message to a topic with message limit enforcement"""
    user_id = request.userId
    logger.debug(
        f"Received message request for topic: {topic_name} from user: {user_id}"
    )

    # Verify user permissions if authenticated
    if current_user is not None and current_user.id != user_id:
        logger.warning(f"User {current_user.id} attempted to post as {user_id}")
        raise HTTPException(
            status_code=403, detail="Cannot post messages as another user"
        )

    # Check if user has reached message limit
    try:
        # Find out actual message count - pass the test limit
        from ..services.message_service import count_user_messages

        user_message_count = await count_user_messages(user_id, test_limit)

        # Use test_limit if provided, otherwise get from config
        current_limit = test_limit if test_limit is not None else get_message_limit()

        # Add debug logging
        logger.debug(
            f"Using message limit: {current_limit} (test override: {test_limit is not None})"
        )

        logger.info(
            f"User {user_id} has {user_message_count} messages (limit: {current_limit})"
        )

        # Strictly enforce limit
        if user_message_count >= current_limit:
            logger.warning(
                f"REJECTED: User {user_id} has reached the message limit of {current_limit}"
            )

            # Ensure we raise the exception here to prevent further processing
            raise HTTPException(
                status_code=429,  # Too Many Requests
                detail=f"User has reached the maximum limit of {current_limit} messages",
            )
    except HTTPException:
        # Re-raise HTTPException - this is important to make sure it propagates
        raise
    except Exception as e:
        # Log other errors but don't block the message
        logger.error(f"Error checking message count for user {user_id}: {e}")

    # Create topic if it doesn't exist
    if topic_name not in topics:
        topics[topic_name] = BaseTopic(topic_name)
        logger.debug(f"Created new topic: {topic_name}")

    # Handle None metadata by defaulting to empty dict
    metadata = request.metadata if request.metadata is not None else {}

    message = Message(
        id=str(uuid.uuid4()),
        content=request.content,
        userId=user_id,
        timestamp=datetime.now(),
        metadata=metadata,
    )

    await topics[topic_name].add_message(message)
    return message


@router.delete(
    "/{topic_name}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_message(
    topic_name: str = Path(..., description="Name of the topic"),
    message_id: str = Path(..., description="ID of the message to delete"),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Delete a specific message.

    Only the message creator can delete their own messages.
    """
    # First, get the message to check ownership
    message = await message_service.get_message(message_id, topic_name)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found in topic {topic_name}",
        )

    # Check if current user is the message creator
    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages",
        )

    # Delete the message
    deleted = await message_service.delete_message(message_id, topic_name)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message",
        )

    # Return 204 No Content status code (handled by FastAPI)
    return None
