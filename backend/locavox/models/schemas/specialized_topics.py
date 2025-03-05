"""
Specialized topic types that inherit from BaseTopic.
These provide specific functionality for different community needs.
"""

from .topic import BaseTopic
from ..logger import setup_logger

logger = setup_logger(__name__)


class EventsTopic(BaseTopic):
    """
    A topic specialized for community events.
    Can include additional features like event dates, locations, etc.
    """

    def __init__(self, name="events"):
        super().__init__(name=name, description="Community events and gatherings")
        self.type = "events"

    async def add_message(self, message):
        """Add a message with event-specific handling"""
        # Here we could add specialized handling for event messages
        logger.info(f"Adding event message to {self.name}")
        return await super().add_message(message)


class MarketplaceTopic(BaseTopic):
    """
    A topic specialized for community marketplace items.
    Can include features like item prices, availability, etc.
    """

    def __init__(self, name="marketplace"):
        super().__init__(
            name=name, description="Community marketplace for goods and services"
        )
        self.type = "marketplace"

    async def add_message(self, message):
        """Add a message with marketplace-specific handling"""
        # Here we could add specialized handling for marketplace listings
        logger.info(f"Adding marketplace listing to {self.name}")
        return await super().add_message(message)


class DiscussionTopic(BaseTopic):
    """
    A topic specialized for general discussions.
    Can include features like categories, tags, etc.
    """

    def __init__(self, name="discussion"):
        super().__init__(name=name, description="Community discussions and forums")
        self.type = "discussion"
