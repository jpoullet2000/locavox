from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from ..services.topics import (
    get_topics as db_get_topics,
    create_topic,
    update_topic,
    delete_topic,
)

# Import the function from topic_registry directly
from ..topic_registry import get_topic_by_id as registry_get_topic_by_id
from ..services.auth_service import get_current_user
from ..models.sql.user import User
from ..models.schemas.topic import TopicCreate, TopicUpdate
from ..models.schemas import Message, TopicBase
from ..services import message_service, auth_service
from ..logger import setup_logger
import uuid
from datetime import datetime
from ..config_helpers import get_message_limit
from ..topic_registry import get_topics as get_topic_registry
from sqlalchemy.ext.asyncio import AsyncSession
from locavox.database import get_db_session

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
    topics = await db_get_topics(skip=skip, limit=limit)

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
    if not current_user.is_superuser:
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
    # This should call the async function from db.topics
    topic = await db_get_topics.get_topic_by_id(topic_id)

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
    if not current_user.is_superuser:
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
    if not current_user.is_superuser:
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


@router.get("/{topic_id}/messages", response_model=List[dict])
async def get_topic_messages(
    topic_id: str = Path(..., description="The ID of the topic"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(auth_service.get_current_user_optional),
):
    """
    Get messages for a specific topic.

    Results are returned in reverse chronological order (newest first).
    """
    logger.info(f"Getting messages for topic {topic_id}")

    # Use the non-async function from topic_registry
    topic = registry_get_topic_by_id(topic_id)

    if not topic:
        logger.warning(f"Topic with ID {topic_id} not found")
        raise HTTPException(status_code=404, detail="Topic not found")

    try:
        messages = await topic.get_messages(
            skip=skip, limit=limit, current_user=current_user
        )
        return messages
    except AttributeError as e:
        logger.error(f"Error getting messages from topic {topic_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The topic does not support retrieving messages",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error getting messages from topic {topic_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}",
        )


@router.post("/{topic_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_topic_message(
    message: dict,
    topic_id: str = Path(..., description="The ID of the topic"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Post a new message to a topic.

    This endpoint requires authentication.
    """
    logger.info(f"Creating message in topic {topic_id}")

    # Use the non-async function from topic_registry
    topic = registry_get_topic_by_id(topic_id)

    if not topic:
        logger.warning(f"Topic with ID {topic_id} not found")
        raise HTTPException(status_code=404, detail="Topic not found")

    # Add the user ID to the message
    message["user_id"] = current_user.id

    try:
        # Use the topic-specific creation logic
        result = await topic.create_message(message, current_user)
        return result
    except AttributeError as e:
        logger.error(f"Error creating message in topic {topic_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The topic does not support creating messages",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating message in topic {topic_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}",
        )


@router.delete(
    "/{topic_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_message(
    topic_id: str = Path(..., description="The ID of the topic"),
    message_id: str = Path(..., description="ID of the message to delete"),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Delete a specific message.

    Only the message creator can delete their own messages.
    """
    # First, get the message to check ownership
    message = await message_service.get_message(message_id, topic_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found in topic {topic_id}",
        )

    # Check if current user is the message creator
    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages",
        )

    # Delete the message
    deleted = await message_service.delete_message(message_id, topic_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message",
        )

    # Return 204 No Content status code (handled by FastAPI)
    return None
