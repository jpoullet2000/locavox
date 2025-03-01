from typing import Dict, List, Union, Any
import lancedb
import os
import pyarrow as pa
import json
import numpy as np
from datetime import datetime
from .base_models import Message  # Updated import
from . import config
from .embeddings import EmbeddingGenerator
from .logger import setup_logger
import asyncio
import pathlib

# Set up logger for this module
logger = setup_logger(__name__)


class TopicStorage:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        # Make sure to use absolute paths to avoid relative path issues
        self.db_path = os.path.abspath(
            os.path.join(config.DATABASE_PATH, topic_name.lower().replace(" ", "_"))
        )
        self.table_name = "messages"
        self.db = None
        self.table = None
        self.embedding_generator = EmbeddingGenerator()
        self._initialized = False

        # Get vector dimension based on selected model
        self.vector_dim = (
            config.OPENAI_EMBEDDING_DIMENSION
            if config.EMBEDDING_MODEL == config.EmbeddingModel.OPENAI
            else config.SENTENCE_TRANSFORMER_DIMENSION
        )

        # Create schema for the table
        self._schema = pa.schema(
            [
                ("id", pa.string()),
                ("content", pa.string()),
                ("userId", pa.string()),
                ("timestamp", pa.timestamp("us")),
                ("metadata", pa.string()),
                (
                    "vector",
                    pa.list_(pa.float32()),
                ),  # Changed from fixed_size_list to list_
            ]
        )
        self.similarity_threshold = 0.1  # Vector similarity threshold
        self.text_match_threshold = 0  # Text match threshold

    def _create_empty_table(self):
        """Create an empty table with the correct schema"""
        # Create an empty vector with proper dimension
        empty_vector = [[0.0] * self.vector_dim]  # Single row with zeros

        arrays = [
            pa.array(["dummy"]),  # id
            pa.array(["dummy"]),  # content
            pa.array(["dummy"]),  # userId
            pa.array([datetime.now()]),  # timestamp
            pa.array(['{"dummy": true}']),  # metadata
            pa.array(empty_vector, type=pa.list_(pa.float32())),  # vector
        ]

        return pa.RecordBatch.from_arrays(arrays, schema=self._schema)

    def _clear_dummy_data(self):
        """Remove the dummy record used for initialization"""
        if self.table:
            # Delete where id='dummy'
            try:
                self.table.delete('id = "dummy"')
            except Exception as e:
                logger.warning(f"Could not delete dummy data: {e}")

    async def _create_or_connect_db(self):
        """Create or connect to the database"""
        try:
            # Ensure the directory exists
            os.makedirs(self.db_path, exist_ok=True)

            # Connect to the database
            self.db = lancedb.connect(self.db_path)
            return self.db
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    async def _create_or_connect_table(self):
        """Create or connect to the table"""
        try:
            # First make sure we have a database
            if not self.db:
                self.db = await self._create_or_connect_db()

            # Check if table exists
            table_path = os.path.join(self.db_path, self.table_name + ".lance")

            if pathlib.Path(table_path).exists():
                # Table exists, connect to it
                self.table = self.db.open_table(self.table_name)
                logger.debug(f"Connected to existing table {self.table_name}")
            else:
                # Table doesn't exist, create it
                empty_batch = self._create_empty_table()
                self.table = self.db.create_table(
                    self.table_name, data=empty_batch, mode="create"
                )
                logger.debug(f"Created new table {self.table_name}")
                # Clear the dummy data
                self._clear_dummy_data()

            return self.table
        except Exception as e:
            logger.error(f"Error creating/connecting to table: {e}")
            raise

    async def initialize(self):
        """Initialize the storage for the topic"""
        try:
            # Connect to the database and table
            await self._create_or_connect_db()
            await self._create_or_connect_table()

            self._initialized = True
            return self
        except Exception as e:
            logger.error(f"Error initializing storage for {self.topic_name}: {e}")
            # Set to not initialized so we can retry later
            self._initialized = False
            raise

    def initialize_sync(self):
        """Synchronous wrapper for initialize"""
        try:
            # Create the event loop or use existing one
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()

            # Run the async initialization function
            if loop.is_running():
                # We're in an async context, create a task
                future = asyncio.ensure_future(self.initialize())
                # We can't await, so we'll have to rely on the task completing later
                # This is not ideal but sometimes necessary
                logger.warning(
                    "initialize_sync called in async context - initialization may not be complete"
                )
            else:
                # We can run the loop to completion
                loop.run_until_complete(self.initialize())

            return self
        except Exception as e:
            logger.error(f"Error in initialize_sync: {e}")
            self._initialized = False
            raise

    async def _ensure_initialized(self):
        """Ensure the storage is initialized"""
        if not self._initialized or not self.table:
            await self.initialize()
        return self._initialized

    async def add_message(self, message: Union[Dict, Message]):
        """Add a message to the storage"""
        # Make sure we're initialized
        await self._ensure_initialized()

        message_dict = (
            message.model_dump() if isinstance(message, Message) else message.copy()
        )

        # Ensure vector is a list of float32
        vector = np.array(
            self.embedding_generator.generate(message_dict["content"]), dtype=np.float32
        )

        # Ensure vector dimension is correct
        if len(vector) != self.vector_dim:
            raise ValueError(
                f"Vector dimension mismatch. Expected {self.vector_dim}, got {len(vector)}"
            )

        # Convert single values to arrays for PyArrow
        prepared_data = {
            "id": [message_dict["id"]],  # Wrap in list
            "content": [message_dict["content"]],  # Wrap in list
            "userId": [message_dict["userId"]],  # Wrap in list
            "timestamp": [message_dict["timestamp"]],  # Wrap in list
            "metadata": [json.dumps(message_dict.get("metadata", {}))],  # Wrap in list
            "vector": [vector.tolist()],  # Wrap in list
        }

        # Create PyArrow record batch with schema
        try:
            batch = pa.RecordBatch.from_pydict(prepared_data, schema=self._schema)
            self.table.add(batch)
        except Exception as e:
            logger.error(f"Error adding message to storage: {e}")
            raise

    async def search_messages(self, query: str, limit: int = 10) -> List[Message]:
        """Search for messages matching the query"""
        # Make sure we're initialized
        await self._ensure_initialized()

        try:
            # Try to get pandas DataFrame from table - handle empty tables
            try:
                df = self.table.to_pandas()
                if df.empty:
                    return []
            except Exception as e:
                logger.warning(f"Error fetching data as pandas DataFrame: {e}")
                return []

            # Calculate text search scores
            df["text_score"] = df["content"].apply(
                lambda x: self._text_search_score(x, query)
            )

            # Get exact matches first
            exact_matches = df[df["text_score"] > 0.8]
            if not exact_matches.empty:
                messages = []
                for _, row in exact_matches.head(limit).iterrows():
                    data = row.to_dict()
                    try:
                        data["metadata"] = json.loads(data["metadata"])
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse message metadata: {e}")
                        data["metadata"] = {}
                    data["embedding"] = data.pop("vector")
                    messages.append(Message(**data))
                return messages

            # If no exact matches, try vector search
            query_vector = np.array(
                self.embedding_generator.generate(query), dtype=np.float32
            ).tolist()

            # Try vector search but handle errors
            try:
                vector_results = (
                    self.table.search(query_vector)
                    .metric("cosine")
                    .nprobes(10)
                    .limit(len(df))
                    .to_pandas()
                )
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")
                return []

            if not vector_results.empty:
                df["vector_score"] = 1 - vector_results["_distance"]
                df["final_score"] = df["text_score"] * 0.7 + df["vector_score"] * 0.3

                # Filter and sort results
                df = df[df["final_score"] >= self.similarity_threshold]
                df = df.sort_values("final_score", ascending=False)

                messages = []
                for _, row in df.head(limit).iterrows():
                    data = row.to_dict()
                    try:
                        data["metadata"] = json.loads(data["metadata"])
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse message metadata: {e}")
                        data["metadata"] = {}
                    data["embedding"] = data.pop("vector")
                    messages.append(Message(**data))
                return messages

            return []
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get all messages, newest first"""
        # Make sure we're initialized
        await self._ensure_initialized()

        try:
            # Try different approaches to fetch data, handling potential errors
            try:
                # First try to get data as pandas DataFrame
                df = (
                    self.table.to_pandas()
                    .sort_values("timestamp", ascending=False)
                    .head(limit)
                )
                results = df.to_dict("records")
            except Exception as e:
                logger.warning(
                    f"Error fetching data as pandas DataFrame: {e}, trying arrow method"
                )

                # Try alternate method with arrow
                try:
                    # Use LanceDB's arrow interface directly
                    query_result = (
                        await self.table.query()
                        .limit(limit)
                        .sort_by("timestamp", ascending=False)
                        .to_arrow()
                    )
                    results = [row._asdict() for row in query_result.to_pylist()]
                except Exception as e2:
                    logger.error(f"Error fetching data with arrow: {e2}")
                    return []

            # Convert string metadata back to dict
            messages = []
            for result in results:
                try:
                    if result["metadata"]:
                        try:
                            result["metadata"] = json.loads(result["metadata"])
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse message metadata: {e}")
                            result["metadata"] = {}
                    messages.append(Message(**result))
                except Exception as e:
                    logger.warning(f"Error processing message data: {e}")
                    # Skip malformed messages

            return messages
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []

    async def get_messages_by_user(
        self, user_id: str, limit: int = 100
    ) -> List[Message]:
        """Get messages from a specific user"""
        # Make sure we're initialized
        await self._ensure_initialized()

        try:
            logger.debug(
                f"Getting messages for user {user_id} in topic {self.topic_name}"
            )

            # Try method 1: Using search with where clause
            try:
                # Fix: Use exact field name "userId" (case sensitive)
                query = (
                    self.table.search().where(f"\"userId\" = '{user_id}'").limit(limit)
                )
                result_df = query.to_pandas()

                if result_df.empty:
                    logger.debug(
                        f"No messages found for user {user_id} in {self.topic_name}"
                    )
                    return []

                messages = []
                for _, row in result_df.iterrows():
                    try:
                        data = row.to_dict()
                        if data["metadata"]:
                            try:
                                data["metadata"] = json.loads(data["metadata"])
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse message metadata: {e}")
                                data["metadata"] = {}
                        messages.append(Message(**data))
                    except Exception as e:
                        logger.warning(f"Error processing message data: {e}")
                        # Skip malformed messages

                logger.debug(f"Found {len(messages)} messages for user {user_id}")
                return messages

            except Exception as e:
                logger.warning(f"Method 1 failed: {e}, trying method 2")

                # Try method 2 with alternative syntax
                try:
                    # Use different syntax with double quotes for field name
                    query = (
                        self.table.search()
                        .where('userId = "{}"'.format(user_id))
                        .limit(limit)
                    )
                    result_df = query.to_pandas()

                    if not result_df.empty:
                        messages = []
                        for _, row in result_df.iterrows():
                            try:
                                data = row.to_dict()
                                if data["metadata"]:
                                    data["metadata"] = json.loads(data["metadata"])
                                messages.append(Message(**data))
                            except Exception as e:
                                logger.warning(f"Error processing message: {e}")

                        logger.debug(f"Method 2 found {len(messages)} messages")
                        return messages
                except Exception as e2:
                    logger.warning(
                        f"Method 2 also failed: {e2}, falling back to full scan"
                    )

                # Method 3: Get all messages and filter in Python
                all_messages = await self.get_messages(
                    1000
                )  # Increased limit for filtering
                user_messages = [msg for msg in all_messages if msg.userId == user_id][
                    :limit
                ]

                logger.debug(
                    f"Method 3: Found {len(user_messages)} messages for user {user_id}"
                )
                return user_messages

        except Exception as e:
            logger.error(f"Failed to get messages for user {user_id}: {e}")
            return []

    def _text_search_score(self, content: str, query: str) -> float:
        """Calculate text match score with exact and partial matching"""
        try:
            content_lower = content.lower()
            query_lower = query.lower()
            query_words = query_lower.split()

            # Exact phrase match gets highest score
            if query_lower in content_lower:
                position = content_lower.index(query_lower)
                # Higher score if match is at start of content
                return 1.0 if position == 0 else 0.9

            # For single-word queries, be more strict
            if len(query_words) == 1:
                return 1.0 if query_lower in content_lower.split() else 0.0

            # For multi-word queries, check word overlap
            content_words = content_lower.split()
            matches = sum(1 for word in query_words if word in content_words)
            return matches / len(query_words) if matches > 0 else 0.0
        except Exception as e:
            logger.warning(f"Error calculating text search score: {e}")
            return 0.0
