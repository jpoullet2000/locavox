# This file makes the directory a proper Python package
# Import all models to be available when importing from .models

from .topic import TopicBase
from .message import Message

# Export commonly used models
__all__ = [
    "TopicBase",
    "Message",
]
