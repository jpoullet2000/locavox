import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.sql.topic import Topic
from ..models.schemas.topic import TopicCreate, TopicUpdate
from ..database import get_db_session
from ..logger import setup_logger

logger = setup_logger(__name__)


async def get_topics(skip: int = 0, limit: int = 100) -> List[Topic]:
    """
    Retrieve topics from the database with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Topic objects
    """
    async for session in get_db_session():
        try:
            query = select(Topic).offset(skip).limit(limit)
            result = await session.execute(query)
            topics = result.scalars().all()
            return topics
        except Exception as e:
            logger.error(f"Error retrieving topics: {str(e)}")
            return []


async def get_topic_by_id(topic_id: str) -> Optional[Topic]:
    """
    Retrieve a specific topic by ID.

    Args:
        topic_id: The ID of the topic to retrieve

    Returns:
        Topic object if found, None otherwise
    """
    async for session in get_db_session():
        try:
            query = select(Topic).where(Topic.id == topic_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error retrieving topic {topic_id}: {str(e)}")
            return None


async def create_topic(topic_data: TopicCreate) -> Topic:
    """
    Create a new topic in the database.

    Args:
        topic_data: TopicCreate object with the data for the new topic

    Returns:
        Created Topic object
    """
    async for session in get_db_session():
        try:
            # Convert Pydantic model to SQL model
            new_topic = Topic(
                title=topic_data.title,
                description=topic_data.description,
                category=topic_data.category,
                image_url=topic_data.image_url,
            )

            session.add(new_topic)
            await session.commit()
            await session.refresh(new_topic)
            return new_topic
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating topic: {str(e)}")
            raise


async def update_topic(topic_id: str, topic_update: TopicUpdate) -> Optional[Topic]:
    """
    Update an existing topic.

    Args:
        topic_id: ID of the topic to update
        topic_update: TopicUpdate object with the updated data

    Returns:
        Updated Topic object if found and updated, None otherwise
    """
    async for session in get_db_session():
        try:
            # First, get the existing topic
            topic = await get_topic_by_id(topic_id)

            if not topic:
                return None

            # Update topic fields
            update_data = topic_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                # Convert snake_case to camelCase for 'image_url' field from API
                if key == "image_url":
                    setattr(topic, "image_url", value)
                else:
                    setattr(topic, key, value)

            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            return topic

        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating topic {topic_id}: {str(e)}")
            return None


async def delete_topic(topic_id: str) -> bool:
    """
    Delete a topic from the database.

    Args:
        topic_id: ID of the topic to delete

    Returns:
        True if the topic was successfully deleted, False otherwise
    """
    async for session in get_db_session():
        try:
            # First check if topic exists
            topic = await get_topic_by_id(topic_id)

            if not topic:
                return False

            # Delete the topic
            await session.delete(topic)
            await session.commit()
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting topic {topic_id}: {str(e)}")
            return False
