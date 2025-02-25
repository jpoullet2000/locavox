import lancedb
import openai
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class TopicStorage:
    def __init__(self, topic_name: str):
        self.db = lancedb.connect("/home/jbp/projects/locavox/data/messagedb")
        self.topic_name = topic_name
        self.table = self._get_or_create_table()

    def _get_or_create_table(self):
        table_name = f"topic_{self.topic_name.lower().replace(' ', '_')}"
        if table_name in self.db.table_names():
            return self.db[table_name]

        schema = {
            "id": "string",
            "content": "string",
            "userId": "string",
            "timestamp": "string",
            "metadata": "json",
            "embedding": "vector[1536]",  # OpenAI embedding dimension
        }
        return self.db.create_table(table_name, schema=schema)

    async def _create_embedding(self, text: str) -> list[float]:
        response = await openai.Embedding.acreate(
            model="text-embedding-ada-002", input=text
        )
        return response.data[0].embedding

    async def add_message(self, message: dict) -> None:
        embedding = await self._create_embedding(message["content"])
        data = {
            **message,
            "timestamp": message["timestamp"].isoformat(),
            "embedding": embedding,
        }
        self.table.add([data])

    async def search_messages(self, query: str, limit: int = 5) -> list[dict]:
        query_embedding = await self._create_embedding(query)
        results = self.table.search(query_embedding).limit(limit).to_list()

        # Convert results back to the expected format
        messages = []
        for r in results:
            msg = {
                "id": r["id"],
                "content": r["content"],
                "userId": r["userId"],
                "timestamp": datetime.fromisoformat(r["timestamp"]),
                "metadata": r["metadata"],
            }
            messages.append(msg)

        return messages
