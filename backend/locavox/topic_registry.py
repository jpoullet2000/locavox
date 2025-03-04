"""
Central registry for topics to avoid circular imports
"""

from typing import Dict
from .models import BaseTopic

# Initialize topics with default topics
_topics = {}


def get_topics() -> Dict[str, BaseTopic]:
    """
    Get the global topics dictionary
    """
    return _topics
