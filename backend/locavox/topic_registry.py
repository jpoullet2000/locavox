"""
A global registry for topics in the application.
This allows different parts of the app to access the same topics.
"""

import uuid
from typing import Dict, Any, Optional
from .models.schemas import TopicBase
from .logger import setup_logger

logger = setup_logger(__name__)

# Dictionary to store all topics by UUID
topics = {}


def get_topics() -> Dict[str, TopicBase]:
    """Get the topics registry"""
    return topics


def add_topic(name: str, topic: Any) -> Any:
    """
    Add a topic to the registry with a UUID

    Args:
        name: Name of the topic
        topic: Topic instance

    Returns:
        The topic instance
    """
    # Generate a UUID for the topic
    topic_id = str(uuid.uuid4())

    # Set the ID on the topic object if it has an id attribute
    if hasattr(topic, "id"):
        topic.id = topic_id

    # Store the topic in the registry using its UUID
    topics[topic_id] = topic

    # Also store a reference by name for backward compatibility
    topics[name] = topic

    logger.info(f"Added topic '{name}' with ID {topic_id}")
    return topic


def get_topic(name: str) -> Optional[Any]:
    """Get a topic by name"""
    return topics.get(name)


def remove_topic(name_or_id: str) -> bool:
    """Remove a topic from the registry by name or ID"""
    if name_or_id in topics:
        del topics[name_or_id]
        return True
    return False


def clear_topics() -> bool:
    """Clear all topics from the registry"""
    topics.clear()
    return True


def get_topic_by_id(topic_id: str) -> Optional[Any]:
    """
    Get a topic by its ID.

    Args:
        topic_id: The UUID of the topic

    Returns:
        Topic instance or None if not found
    """
    return topics.get(topic_id)


def get_topic_by_name(topic_name: str) -> Optional[Any]:
    """
    Get a topic by its name or title.

    Args:
        topic_name: The name of the topic

    Returns:
        Topic instance or None if not found
    """
    # First check direct match
    if topic_name in topics:
        return topics[topic_name]

    # Otherwise check by title attribute
    for topic in topics.values():
        if hasattr(topic, "title") and topic.title.lower() == topic_name.lower():
            return topic

    return None
