from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

from models import Message, CommunityTaskMarketplace, NeighborhoodHubChat

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize topics
topics = {"marketplace": CommunityTaskMarketplace(), "chat": NeighborhoodHubChat()}


class QueryRequest(BaseModel):
    query: str


class MessageRequest(BaseModel):
    userId: str
    content: str
    metadata: Optional[dict] = None


@app.post("/query")
async def query_topics(request: QueryRequest):
    # TODO: Implement LLM logic here
    # For now, simple keyword matching
    query = request.query.lower()
    for topic in topics.values():
        matching_messages = [
            msg
            for msg in topic.messages
            if any(kw in msg.content.lower() for kw in query.split())
        ]
        if matching_messages:
            return {
                "topic": {"name": topic.name, "description": topic.description},
                "messages": matching_messages,
            }
    return None


@app.post("/topics/{topic_name}/messages")
async def add_message(topic_name: str, request: MessageRequest):
    topic = next(
        (t for t in topics.values() if t.name.lower() == topic_name.lower()), None
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    message = Message(
        id=str(uuid.uuid4()),
        content=request.content,
        userId=request.userId,
        timestamp=datetime.now(),
        metadata=request.metadata,
    )
    topic.add_message(message)
    return message
