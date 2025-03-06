import uuid
from typing import List, Optional
from ..models.schemas.topic import TopicCreate, TopicUpdate

# In-memory topic store for demonstration
topics_db = {}


async def get_topics(skip: int = 0, limit: int = 100) -> List:
    """
    Get a list of all topics

    Args:
        skip: Number of topics to skip
        limit: Maximum number of topics to return

    Returns:
        List of topic objects
    """
    topics = list(topics_db.values())
    return topics[skip : skip + limit]


async def get_topic_by_id(topic_id: str) -> Optional[dict]:
    """
    Get a topic by ID

    Args:
        topic_id: UUID of the topic

    Returns:
        Topic object or None if not found
    """
    return topics_db.get(topic_id)


async def create_topic(topic: TopicCreate) -> dict:
    """
    Create a new topic

    Args:
        topic: Topic creation data

    Returns:
        Created topic object
    """
    # Generate UUID for the topic
    topic_id = str(uuid.uuid4())

    topic_dict = topic.model_dump()
    topic_dict["id"] = topic_id
    topic_dict["image_url"] = topic_dict.pop(
        "imageUrl", None
    )  # Convert to snake_case for storage

    # Store in our in-memory DB
    topics_db[topic_id] = topic_dict

    return topic_dict


async def update_topic(topic_id: str, topic: TopicUpdate) -> Optional[dict]:
    """
    Update an existing topic

    Args:
        topic_id: UUID of the topic
        topic: Topic update data

    Returns:
        Updated topic object or None if not found
    """
    if topic_id not in topics_db:
        return None

    current_topic = topics_db[topic_id]
    update_data = topic.dict(exclude_unset=True)

    # Handle imageUrl conversion to image_url
    if "imageUrl" in update_data:
        update_data["image_url"] = update_data.pop("imageUrl")

    # Update topic fields
    for field, value in update_data.items():
        current_topic[field] = value

    return current_topic


async def delete_topic(topic_id: str) -> bool:
    """
    Delete a topic

    Args:
        topic_id: UUID of the topic

    Returns:
        True if deleted, False if not found
    """
    if topic_id in topics_db:
        del topics_db[topic_id]
        return True
    return False
