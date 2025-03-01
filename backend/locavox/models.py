from typing import List
from datetime import datetime
import uuid

from .base_models import Message
from .storage import TopicStorage
from .logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)


class BaseTopic:
    def __init__(self, name: str, description: str = None):
        self.name = name
        # Use provided description or generate a default one
        self.description = description if description else f"Dynamic topic: {name}"
        self.messages: List[Message] = []
        self.storage = TopicStorage(name)
        # Initialize synchronously in constructor for immediate use
        try:
            self.storage.initialize_sync()
        except Exception as e:
            logger.warning(
                f"Failed to initialize storage synchronously: {e}, will try async later"
            )

    async def initialize(self):
        """Initialize the topic storage"""
        try:
            await self.storage.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            return False

    def initialize_sync(self):
        """Synchronous initialization"""
        self.storage.initialize_sync()
        return self

    async def add_message(self, message: Message):
        """Add a message to this topic"""
        if not self.storage.table:
            await self.storage.initialize()
        await self.storage.add_message(message)
        self.messages.append(message)
        return message

    async def search_messages(self, query: str, limit: int = 10) -> List[Message]:
        """Search messages in this topic by content"""
        if not self.storage.table:
            await self.storage.initialize()
        return await self.storage.search_messages(query, limit)

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get all messages from this topic, newest first"""
        if not self.storage.table:
            await self.storage.initialize()
        return await self.storage.get_messages(limit)

    async def _get_table(self):
        """Get the LanceDB table, initializing if needed"""
        try:
            # Check if the table exists and is initialized
            if not self.storage.table:
                await self.storage.initialize()

            if not self.storage.table:
                raise ValueError(f"Failed to initialize table for topic {self.name}")

            return self.storage.table
        except Exception as e:
            logger.error(f"Error getting table: {e}")
            raise

    async def get_messages_by_user(
        self, user_id: str, limit: int = 100
    ) -> List[Message]:
        """
        Efficiently retrieve messages from a specific user using LanceDB's vector filtering

        Args:
            user_id: The user ID to filter by
            limit: Maximum number of messages to retrieve

        Returns:
            List of Message objects from the specified user
        """
        try:
            # Make sure we're initialized
            await self._ensure_initialized()

            # If still not initialized, try another approach
            if not self.storage.table:
                logger.warning(f"No table available for topic {self.name}")
                return []

            logger.debug(f"Querying messages for user {user_id} in topic {self.name}")

            # First try direct query through storage
            try:
                messages = await self.storage.get_messages_by_user(user_id, limit)
                if messages:
                    logger.debug(f"Found {len(messages)} messages via storage query")
                    return messages
            except Exception as e:
                logger.warning(f"Storage query failed: {e}, trying custom query")

            # Try with Lance where clause
            try:
                # Use LanceDB's where clause for efficient filtering
                # Fix: Use correct case and quoting for field name
                logger.debug("Trying direct LanceDB where clause")
                tbl = self.storage.table
                query = tbl.search().where(f"\"userId\" = '{user_id}'").limit(limit)
                query_result = await query.execute()

                # Convert results to Message objects
                messages = []
                for item in query_result:
                    try:
                        # Extract data from the LanceDB result
                        data = item.to_dict()

                        # Skip malformed entries
                        if "userId" not in data or "content" not in data:
                            continue

                        # Create Message object
                        msg = Message(
                            id=data.get("id", str(uuid.uuid4())),
                            userId=data["userId"],
                            content=data["content"],
                            timestamp=datetime.fromisoformat(data["timestamp"])
                            if "timestamp" in data
                            else datetime.now(),
                            metadata=data.get("metadata", {}),
                        )
                        messages.append(msg)
                    except (KeyError, ValueError, TypeError) as e:
                        logger.error(f"Error processing message data: {e}")
                        # Skip malformed messages

                logger.debug(f"Found {len(messages)} messages via direct where clause")
                return messages

            except Exception as e:
                logger.warning(
                    f"Direct where query failed: {e}, trying final fallback method"
                )

                # Final fallback: get all messages and filter in memory
                all_messages = await self.get_messages(1000)  # Get a large sample
                user_messages = [msg for msg in all_messages if msg.userId == user_id][
                    :limit
                ]
                logger.debug(f"Found {len(user_messages)} messages via full scan")
                return user_messages

        except Exception as e:
            logger.error(
                f"Error retrieving messages by user {user_id} from {self.name}: {e}"
            )
            return []

    async def _ensure_initialized(self):
        """Ensure the topic is initialized"""
        if not self.storage.table:
            logger.debug(f"Initializing storage for topic {self.name}")
            await self.initialize()
        return True  # Return success value


# Topic-specific implementations
class CommunityTaskMarketplace(BaseTopic):
    def __init__(self):
        super().__init__(
            "Community Task Marketplace", "Local tasks and services exchange"
        )


class NeighborhoodHubChat(BaseTopic):
    def __init__(self):
        super().__init__("Neighborhood Hub Chat", "General neighborhood discussions")
