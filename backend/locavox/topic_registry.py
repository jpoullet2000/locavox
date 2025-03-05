"""
A global registry for topics in the application.
This allows different parts of the app to access the same topics.
"""

from typing import Dict
from .models.schemas import BaseTopic

# Dictionary to store all topics by name
topics = {}


def get_topics() -> Dict[str, BaseTopic]:
    """Get the topics registry"""
    return topics


def add_topic(name, topic):
    """Add a topic to the registry"""
    topics[name] = topic
    return topic


def get_topic(name):
    """Get a topic by name"""
    return topics.get(name)


def remove_topic(name):
    """Remove a topic from the registry"""
    if name in topics:
        del topics[name]
        return True
    return False


def clear_topics():
    """Clear all topics from the registry"""
    topics.clear()
    return True
