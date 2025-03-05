import datetime
from typing import List, Optional
import uuid
from ..models.schemas.topic import Topic, TopicCreate, TopicUpdate

# Mock database - replace with actual database in production
topics_db = [
    Topic(
        id="1",
        title="Local Events",
        description="Discover upcoming events in your community.",
        category="Community",
        image_url="https://via.placeholder.com/300x200?text=Events",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
    Topic(
        id="2",
        title="Community Projects",
        description="Learn about and get involved with local community projects.",
        category="Volunteering",
        image_url="https://via.placeholder.com/300x200?text=Projects",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
    Topic(
        id="3",
        title="Local Businesses",
        description="Support local businesses and discover new favorites.",
        category="Business",
        image_url="https://via.placeholder.com/300x200?text=Businesses",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
    Topic(
        id="4",
        title="Neighborhood News",
        description="Stay updated on what's happening in your neighborhood.",
        category="News",
        image_url="https://via.placeholder.com/300x200?text=News",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
]


async def get_topics(skip: int = 0, limit: int = 100) -> List[Topic]:
    """Get all topics with pagination."""
    return topics_db[skip : skip + limit]


async def create_topic(topic_data: TopicCreate) -> Topic:
    """Create a new topic."""
    new_topic = Topic(
        id=str(uuid.uuid4()),
        **topic_data.dict(),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    topics_db.append(new_topic)
    return new_topic


async def get_topic_by_id(topic_id: str) -> Optional[Topic]:
    """Get a specific topic by ID."""
    for topic in topics_db:
        if topic.id == topic_id:
            return topic
    return None


async def update_topic(topic_id: str, topic_update: TopicUpdate) -> Optional[Topic]:
    """Update a specific topic."""
    for i, topic in enumerate(topics_db):
        if topic.id == topic_id:
            update_data = topic_update.dict(exclude_unset=True)
            updated_topic = topic.copy()

            for key, value in update_data.items():
                if value is not None:
                    setattr(updated_topic, key, value)

            updated_topic.updated_at = datetime.datetime.now()
            topics_db[i] = updated_topic
            return updated_topic
    return None


async def delete_topic(topic_id: str) -> bool:
    """Delete a specific topic."""
    for i, topic in enumerate(topics_db):
        if topic.id == topic_id:
            topics_db.pop(i)
            return True
    return False
