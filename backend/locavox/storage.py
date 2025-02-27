import asyncio
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


class TopicStorage:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.db_path = os.path.join(
            config.DATABASE_PATH, topic_name.lower().replace(" ", "_")
        )
        self.table_name = "messages"
        self.db = None
        self.table = None
        self.embedding_generator = EmbeddingGenerator()

        # Get vector dimension based on selected model
        self.vector_dim = (
            config.OPENAI_EMBEDDING_DIMENSION
            if config.EMBEDDING_MODEL == config.EmbeddingModel.OPENAI
            else config.SENTENCE_TRANSFORMER_DIMENSION
        )

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
            self.table.delete('id = "dummy"')

    async def initialize(self):
        """Initialize the storage for the topic"""
        if not self.db:
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)

        empty_batch = self._create_empty_table()

        self.table = self.db.create_table(
            self.table_name, data=empty_batch, mode="overwrite"
        )

        self._clear_dummy_data()
        return self

    def initialize_sync(self):
        """Synchronous wrapper for initialize"""
        if not self.db:
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)

        empty_batch = self._create_empty_table()

        self.table = self.db.create_table(
            self.table_name, data=empty_batch, mode="overwrite"
        )

        self._clear_dummy_data()
        return self

    def _message_to_dict(self, message: "Message") -> Dict[str, Any]:
        """Convert message to database-friendly format"""
        import json

        return {
            "id": message.id,
            "content": message.content,
            "userId": message.userId,
            "timestamp": message.timestamp,
            "metadata": json.dumps(message.metadata),
        }

    def _dict_to_message(self, data: Dict[str, Any]) -> "Message":
        """Convert database format back to Message"""
        import json
        from locavox.base_models import Message

        if isinstance(data["metadata"], str):
            data["metadata"] = json.loads(data["metadata"])
        return Message(**data)

    async def add_message(self, message: Union[Dict, Message]):
        if not self.table:
            await self.initialize()

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
        batch = pa.RecordBatch.from_pydict(prepared_data, schema=self._schema)
        self.table.add(batch)

    def _text_search_score(self, content: str, query: str) -> float:
        """Calculate text match score with exact and partial matching"""
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

    async def search_messages(self, query: str, limit: int = 10) -> List[Message]:
        if not self.table:
            await self.initialize()

        df = self.table.to_pandas()
        if df.empty:
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
                data["metadata"] = json.loads(data["metadata"])
                data["embedding"] = data.pop("vector")
                messages.append(Message(**data))
            return messages

        # If no exact matches, try vector search
        query_vector = np.array(
            self.embedding_generator.generate(query), dtype=np.float32
        ).tolist()
        vector_results = (
            self.table.search(query_vector)
            .metric("cosine")
            .nprobes(10)
            .limit(len(df))
            .to_pandas()
        )

        if not vector_results.empty:
            df["vector_score"] = 1 - vector_results["_distance"]
            df["final_score"] = df["text_score"] * 0.7 + df["vector_score"] * 0.3

            # Filter and sort results
            df = df[df["final_score"] >= self.similarity_threshold]
            df = df.sort_values("final_score", ascending=False)

            messages = []
            for _, row in df.head(limit).iterrows():
                data = row.to_dict()
                data["metadata"] = json.loads(data["metadata"])
                data["embedding"] = data.pop("vector")
                messages.append(Message(**data))
            return messages

        return []

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get all messages from the topic, newest first."""
        if not self.table:
            await self.initialize()

        df = (
            self.table.to_pandas().sort_values("timestamp", ascending=False).head(limit)
        )

        results = df.to_dict("records")

        # Convert string metadata back to dict
        for result in results:
            if result["metadata"]:
                try:
                    result["metadata"] = json.loads(result["metadata"])
                except:
                    result["metadata"] = {}

        return [Message(**result) for result in results]
