import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv
from . import config  # Import config first

from .models import (
    Message,
    CommunityTaskMarketplace,
    NeighborhoodHubChat,
    Topic,  # Add Topic to imports
)  # Use relative import

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

dot_env_file = os.getenv("LOCAVOX_DOT_ENV_FILE", ".env")
load_dotenv(dotenv_path=dot_env_file)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize topics after environment is set up
topics = None


@app.on_event("startup")
async def startup_event():
    global topics
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


# Add a debug endpoint to list messages in a topic
@app.get("/topics/{topic_name}/messages")
async def list_messages(topic_name: str):
    if topic_name not in topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    messages = await topics[topic_name].get_messages(10)
    return {"messages": [msg.model_dump() for msg in messages]}
