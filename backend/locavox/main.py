from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import logging

from .models import (
    Message,
    CommunityTaskMarketplace,
    NeighborhoodHubChat,
    Topic,  # Add Topic to imports
)  # Use relative import

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
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
    logger.debug(f"Received message request for topic: {topic_name}")

    # Create topic if it doesn't exist
    if topic_name not in topics:
        topics[topic_name] = Topic(topic_name)
        logger.debug(f"Created new topic: {topic_name}")

    message = Message(
        id=str(uuid.uuid4()),
        content=request.content,
        userId=request.userId,
        timestamp=datetime.now(),
        metadata=request.metadata,
    )
    topics[topic_name].add_message(message)
    return message


# Add a debug endpoint to list available topics
@app.get("/topics")
async def list_topics():
    return {"topics": list(topics.keys())}
