from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from ..db.topics import (
    get_topics,
    create_topic,
    get_topic_by_id,
    update_topic,
    delete_topic,
)
from ..services.auth_service import get_current_user
from ..models.user import User
from ..models.topic import TopicCreate, TopicUpdate
from ..models import Message, BaseTopic
from ..services import message_service, auth_service
from ..logger import setup_logger
import uuid
from datetime import datetime
from ..config_helpers import get_message_limit
from ..topic_registry import get_topics as get_topic_registry

# Set up logger for this module
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
    responses={404: {"description": "Not found"}},
)

topic_registry = get_topic_registry()


# Response model definitions (from endpoints/topics.py)
class TopicResponse(BaseModel):
    id: str
    title: str
    description: str
    category: Optional[str] = None
    imageUrl: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "title": "Local Events",
                "description": "Discover upcoming events in your community",
                "category": "Community",
                "imageUrl": "https://example.com/images/events.jpg",
            }
        }


class TopicsListResponse(BaseModel):
    topics: List[TopicResponse]


class MessageRequest(BaseModel):
    userId: str
    content: str
    metadata: Optional[dict] = None


# Route handlers: TOPIC CRUD OPERATIONS (prioritizing from endpoints/topics.py)


@router.get("/", response_model=List[TopicResponse])
async def read_topics(skip: int = 0, limit: int = 100):
    """
    Retrieve all topics.

    Returns a list of topic objects with full attributes instead of just names.
    """
    topics = await get_topics(skip=skip, limit=limit)

    # Transform the topics into the expected response format
    formatted_topics = [
        TopicResponse(
            id=str(topic.id),
            title=topic.title,
            description=topic.description,
            category=topic.category,
            imageUrl=topic.image_url,
        )
        for topic in topics
    ]

    return formatted_topics


@router.post("/", response_model=TopicResponse)
async def create_new_topic(
    topic: TopicCreate, current_user: User = Depends(get_current_user)
):
    """Create a new topic."""
    breakpoint()
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create topics")

    created_topic = await create_topic(topic)
    return TopicResponse(
        id=str(created_topic.id),
        title=created_topic.title,
        description=created_topic.description,
        category=created_topic.category,
        imageUrl=created_topic.image_url,
    )


@router.get("/{topic_id}", response_model=TopicResponse)
async def read_topic(topic_id: str):
    """Get a specific topic by ID."""
    topic = await get_topic_by_id(topic_id)

    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    return TopicResponse(
        id=str(topic.id),
        title=topic.title,
        description=topic.description,
        category=topic.category,
        imageUrl=topic.image_url,
    )


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_existing_topic(
    topic_id: str,
    topic_update: TopicUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a topic."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update topics")

    updated_topic = await update_topic(topic_id, topic_update)

    if updated_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    return TopicResponse(
        id=str(updated_topic.id),
        title=updated_topic.title,
        description=updated_topic.description,
        category=updated_topic.category,
        imageUrl=updated_topic.image_url,
    )


@router.delete("/{topic_id}", response_model=dict)
async def delete_existing_topic(
    topic_id: str, current_user: User = Depends(get_current_user)
):
    """Delete a topic."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete topics")

    success = await delete_topic(topic_id)

    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")

    return {"message": "Topic deleted successfully"}


# Route handlers: TOPIC REGISTRY & MESSAGES (from original routers/topics.py)


@router.get("/registry", response_model=Dict[str, str])
async def list_topic_registry():
    """List all available topics in the topic registry"""
    if topic_registry is None:
        return {}
    return {name: topic.__class__.__name__ for name, topic in topic_registry.items()}


@router.get("/{topic_name}/messages")
async def list_messages(topic_name: str):
    """Get all messages in a topic"""
    if topic_name not in topic_registry:
        raise HTTPException(status_code=404, detail="Topic not found")
    messages = await topic_registry[topic_name].get_messages(10)
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
    if topic_name not in topic_registry:
        topic_registry[topic_name] = BaseTopic(topic_name)
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

    await topic_registry[topic_name].add_message(message)
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
