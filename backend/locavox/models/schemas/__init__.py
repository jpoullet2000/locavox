# This file makes the directory a proper Python package
# Import all models to be available when importing from .models
# Import Base from base.py to ensure a single shared Base instance

from .base import Base
from .user import User
from .user_address import UserAddress

# Import more models if available
try:
    from .message import Message
    from .topic import BaseTopic
    from .specialized_topics import EventsTopic, MarketplaceTopic, DiscussionTopic
except ImportError:
    pass

# Export commonly used models
__all__ = [
    "Base",
    "User",
    "UserAddress",
]

# Add conditional exports
try:
    __all__.extend(
        [
            "Message",
            "BaseTopic",
            "EventsTopic",
            "MarketplaceTopic",
            "DiscussionTopic",
        ]
    )
except NameError:
    pass
