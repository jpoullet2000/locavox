from typing import Dict, List, Union
import lancedb
import os
import pyarrow as pa
import json
from .base_models import Message  # Updated import


class TopicStorage:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.db_path = os.path.join("data", topic_name.lower().replace(" ", "_"))
        self.table_name = "messages"
        self.db = None
        self.table = None

    def initialize(self):  # Remove async
        """Initialize the storage for the topic"""
        if not self.db:
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)

        # Define schema using PyArrow types
        schema = pa.schema(
            [
                ("id", pa.string()),
                ("content", pa.string()),
                ("userId", pa.string()),
                ("timestamp", pa.timestamp("us")),
                ("metadata", pa.string()),  # Store JSON as string
            ]
        )

        # Always create a fresh table
        import pandas as pd

        empty_df = pd.DataFrame(
            {
                "id": [],
                "content": [],
                "userId": [],
                "timestamp": [],
                "metadata": [],
            }
        ).astype(
            {
                "id": "string",
                "content": "string",
                "userId": "string",
                "timestamp": "datetime64[us]",
                "metadata": "string",
            }
        )

        self.table = self.db.create_table(
            self.table_name,
            data=empty_df,
            mode="overwrite",  # Always overwrite to ensure clean state
        )

        return self

    def add_message(self, message: Union[Dict, Message]):  # Remove async
        if not self.table:
            self.initialize()

        # Convert message to dict if it's a Pydantic model
        if isinstance(message, Message):
            message_dict = message.model_dump()
        else:
            message_dict = message.copy()

        # Convert metadata to JSON string
        if isinstance(message_dict.get("metadata"), dict):
            message_dict["metadata"] = json.dumps(message_dict["metadata"])

        self.table.add([message_dict])  # Remove await

    def search_messages(self, query: str) -> List[Message]:
        if not self.table:
            self.initialize()

        # Use pandas to get unique results
        df = self.table.to_pandas()
        results = (
            df[df["content"].str.contains(query, case=False, na=False)]
            .drop_duplicates(subset=["id"])  # Ensure unique messages by id
            .to_dict("records")
        )

        # Convert string metadata back to dict if needed
        for result in results:
            if result["metadata"]:
                try:
                    result["metadata"] = json.loads(result["metadata"])
                except:
                    result["metadata"] = {}

        return [Message(**result) for result in results[:10]]  # Limit to 10 results
