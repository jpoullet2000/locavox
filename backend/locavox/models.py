import os
import json  # Add import for JSON handling
import asyncio  # Add import for asyncio
from typing import List
from datetime import datetime
import uuid

from .base_models import Message
from .storage import TopicStorage
from .logger import setup_logger

# Import the query builder properly
from locavox.lance_query_builder import LanceEmptyQueryBuilder, LanceComplexQueryBuilder

# Set up logger for this module
logger = setup_logger(__name__)


class BaseTopic:
    def __init__(self, name: str, description: str = None):
        self.name = name
        # Use provided description or generate a default one
        self.description = description if description else f"Dynamic topic: {name}"
        self.messages: List[Message] = []
        self.storage = TopicStorage(name)
        self._init_complete = False

        # Initialize storage based on context
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_event_loop()
                is_running = loop.is_running()
            except RuntimeError:
                is_running = False

            if is_running:
                # In async context, schedule async initialization
                logger.debug(
                    f"In async context - scheduling async initialization for topic {name}"
                )
                # Schedule but don't wait
                asyncio.create_task(self._async_init())
            else:
                # In sync context, initialize synchronously
                logger.debug(
                    f"In sync context - initializing synchronously for topic {name}"
                )
                self.storage.initialize_sync()
                self._init_complete = True
        except Exception as e:
            logger.warning(
                f"Failed to initialize storage: {e}, will initialize on first use"
            )

    async def _async_init(self):
        """Helper method for async initialization"""
        try:
            await self.initialize()
            self._init_complete = True
            logger.debug(f"Async initialization completed for topic {self.name}")
        except Exception as e:
            logger.error(f"Async initialization failed for topic {self.name}: {e}")

    async def initialize(self):
        """Initialize the topic storage"""
        try:
            await self.storage.initialize()
            self._init_complete = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            return False

    def initialize_sync(self):
        """Synchronous initialization"""
        self.storage.initialize_sync()
        self._init_complete = True
        return self

    async def add_message(self, message: Message):
        """Add a message to this topic"""
        # Ensure initialization is complete
        if not self._init_complete or not self.storage.table:
            logger.debug(
                f"Initializing storage for topic {self.name} before adding message"
            )
            await self.initialize()
        await self.storage.add_message(message)
        self.messages.append(message)
        return message

    async def search_messages(self, query: str, limit: int = 10) -> List[Message]:
        """Search messages in this topic by content"""
        # Ensure initialization is complete
        if not self._init_complete or not self.storage.table:
            logger.debug(
                f"Initializing storage for topic {self.name} before searching messages"
            )
            await self.initialize()
        return await self.storage.search_messages(query, limit)

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get all messages from this topic, newest first"""
        # Ensure initialization is complete
        if not self._init_complete or not self.storage.table:
            logger.debug(
                f"Initializing storage for topic {self.name} before getting messages"
            )
            await self.initialize()
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
        Get messages from a specific user with optimized query
        """
        try:
            # Ensure initialization is complete
            if not self._init_complete or not self.storage.table:
                logger.debug(
                    f"Initializing storage for topic {self.name} before querying messages by user"
                )
                await self.initialize()

                # Extra check after initialization
                if not self.storage.table:
                    logger.error("Failed to initialize table in storage")
                    raise ValueError("Could not initialize table")

            # Get the dataset path from storage
            dataset_path = self.storage.dataset_path
            logger.info(f"Using dataset path: {dataset_path}")

            # Check if the dataset path exists before proceeding
            if not os.path.exists(dataset_path):
                logger.warning(f"Dataset path does not exist: {dataset_path}")

                # Try looking for common variations of the path
                parent_dir = os.path.dirname(dataset_path)
                basename = os.path.basename(dataset_path)

                # Look in parent directory for files with similar names
                if os.path.exists(parent_dir):
                    logger.debug(f"Parent directory exists: {parent_dir}")
                    files = os.listdir(parent_dir)
                    logger.debug(f"Files in parent directory: {files}")

                    # Check if there's a similar file we could use
                    for file in files:
                        if basename in file or self.storage.table_name in file:
                            potential_path = os.path.join(parent_dir, file)
                            logger.info(
                                f"Found potential dataset file: {potential_path}"
                            )
                            dataset_path = potential_path
                            break

            # Log the actual db_path, which might be different from dataset_path
            logger.debug(f"Storage db_path: {self.storage.db_path}")

            # Try using the Lance query builder with where condition
            logger.info(f"Creating query builder for {dataset_path}")
            query_builder = LanceEmptyQueryBuilder(dataset_path)
            logger.debug(f"Querying for messages with userId={user_id}")
            results = query_builder.where("userId", user_id).execute()

            if not results:
                logger.warning(
                    f"No results returned from query builder for user {user_id}"
                )

            # Process and convert results to Message objects
            messages = []
            for result in results[:limit]:  # Apply limit after query for simplicity
                try:
                    # Handle the embedding vs vector field name difference
                    if "vector" in result and "embedding" not in result:
                        result["embedding"] = result.pop("vector")

                    # Handle metadata parsing from JSON string if needed
                    if "metadata" in result and isinstance(result["metadata"], str):
                        try:
                            result["metadata"] = json.loads(result["metadata"])
                        except json.JSONDecodeError:
                            result["metadata"] = {}

                    messages.append(Message(**result))
                except Exception as e:
                    logger.error(f"Error converting result to Message: {e}")
                    logger.debug(f"Problematic record: {result}")

            logger.debug(
                f"Found {len(messages)} messages for user {user_id} using query builder"
            )
            return messages

        except Exception as e:
            logger.warning(
                f"Direct where query failed: {e}, trying final fallback method"
            )
            logger.debug(f"Error details: ", exc_info=True)

            # Fallback to retrieving all messages and filtering
            logger.info("Using fallback method: get all messages and filter")
            all_messages = await self.get_messages(1000)  # Get a reasonable batch
            user_messages = [msg for msg in all_messages if msg.userId == user_id]
            logger.info(
                f"Fallback method found {len(user_messages)} messages for user {user_id}"
            )
            return user_messages[:limit]  # Apply the limit

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
