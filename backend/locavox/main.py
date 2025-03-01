import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from . import config  # Import config first
from .logger import setup_logger  # Import our centralized logger
from .config_helpers import get_message_limit  # Import our new helper

# Import models - update to only use BaseTopic
from .models import (
    Message,
    BaseTopic,  # Use BaseTopic instead of Topic
    CommunityTaskMarketplace,
    NeighborhoodHubChat,
)

# Set up logger for this module
logger = setup_logger(__name__)

dot_env_file = os.getenv("LOCAVOX_DOT_ENV_FILE", ".env")
load_dotenv(dotenv_path=dot_env_file)

# Initialize topics at module level with default topics
topics = {"marketplace": CommunityTaskMarketplace(), "chat": NeighborhoodHubChat()}

# Import SmartSearch conditionally - will be done in the query_topics function


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup and shutdown events"""
    # Startup
    global topics
    if topics is None:
        topics = {
            "marketplace": CommunityTaskMarketplace(),
            "chat": NeighborhoodHubChat(),
        }

    # Check OpenAI API key status at startup
    if config.OPENAI_API_KEY:
        logger.info("OpenAI API key found - LLM features will be available")
    else:
        logger.warning("OpenAI API key not set - LLM features will be disabled")

    yield
    # Shutdown
    # Add any cleanup code here if needed


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    use_llm: bool = config.USE_LLM_BY_DEFAULT  # Default from config


class MessageRequest(BaseModel):
    userId: str
    content: str
    metadata: Optional[dict] = None


@app.post("/query")
async def query_topics(request: QueryRequest):
    """Enhanced search across topics with LLM-powered ranking and insights"""
    query = request.query

    # Use LLM only if explicitly requested and API key is available
    use_llm = request.use_llm and config.OPENAI_API_KEY

    if not use_llm:
        # Use search_messages for relevant results without LLM
        for topic_name, topic in topics.items():
            # Use each topic's search_messages method to get relevant results
            relevant_messages = await topic.search_messages(query)

            if relevant_messages:
                return {
                    "topic": {"name": topic.name, "description": topic.description},
                    "messages": relevant_messages,
                    "query": query,
                }
        return {"query": query, "topic": None, "messages": []}
    else:
        # Only import SmartSearch when LLM is requested and API key is available
        try:
            # Conditional import to avoid initialization issues
            from .llm_search import SmartSearch

            results = await SmartSearch.search_all_topics(query, topics)
            return results
        except ImportError as e:
            logger.error(f"Failed to import SmartSearch module: {e}")
            # Fall back to simple search on error
            return await query_topics(QueryRequest(query=query, use_llm=False))
        except Exception as e:
            logger.error(f"LLM search failed: {e}")
            # Fall back to simple search on error
            return await query_topics(QueryRequest(query=query, use_llm=False))


async def count_user_messages(user_id: str, test_limit: Optional[int] = None) -> int:
    """Count the total number of messages from a user across all topics"""
    total_count = 0
    logger.debug(f"Counting messages for user {user_id}")

    # Get the current message limit with possible override
    current_limit = test_limit if test_limit is not None else get_message_limit()

    logger.debug(
        f"Using message limit: {current_limit} (test override: {test_limit is not None})"
    )

    # First try with the direct query
    for topic_name, topic in topics.items():
        try:
            # Get messages for this user in this topic
            user_messages = await topic.get_messages_by_user(user_id, current_limit + 1)
            topic_count = len(user_messages)
            logger.debug(
                f"Found {topic_count} messages in topic {topic_name} for user {user_id}"
            )
            total_count += topic_count

            # If we've already exceeded the limit, we can return early
            if total_count >= current_limit:
                logger.info(
                    f"User {user_id} has reached/exceeded the message limit of {current_limit}"
                )
                return total_count
        except Exception as e:
            logger.error(
                f"Error counting messages for user {user_id} in topic {topic_name}: {e}"
            )
            # Continue with other topics even if one fails

    # Double-check with a full message list if we're getting close to the limit
    if total_count >= current_limit - 2:
        # Let's verify the count with a direct API call to be sure
        manual_count = 0
        for topic_name, topic in topics.items():
            try:
                all_messages = await topic.get_messages(1000)  # Get a larger sample
                user_messages = [msg for msg in all_messages if msg.userId == user_id]
                manual_count += len(user_messages)

                if manual_count >= current_limit:
                    logger.warning(
                        f"Manual count found that user {user_id} has {manual_count} messages, exceeding limit"
                    )
                    return manual_count
            except Exception as e:
                logger.error(f"Error in manual count: {e}")

    logger.debug(f"Final count: User {user_id} has a total of {total_count} messages")
    return total_count


@app.post("/topics/{topic_name}/messages")
async def add_message(
    topic_name: str,
    request: MessageRequest,
    test_limit: Optional[int] = Query(
        None, description="Override message limit for testing"
    ),
):
    """Add a message to a topic with message limit enforcement"""
    user_id = request.userId
    logger.debug(
        f"Received message request for topic: {topic_name} from user: {user_id}"
    )

    # Check if user has reached message limit
    try:
        # Find out actual message count - pass the test limit
        user_message_count = await count_user_messages(user_id, test_limit)

        # Use test_limit if provided, otherwise get from config
        current_limit = test_limit if test_limit is not None else get_message_limit()

        # Add debug logging
        logger.debug(
            f"Using message limit: {current_limit} (test override: {test_limit is not None})"
        )

        logger.info(
            f"User {user_id} has {user_message_count} messages (limit: {current_limit})"
        )

        # Strictly enforce limit
        if user_message_count >= current_limit:
            logger.warning(
                f"REJECTED: User {user_id} has reached the message limit of {current_limit}"
            )

            # Ensure we raise the exception here to prevent further processing
            raise HTTPException(
                status_code=429,  # Too Many Requests
                detail=f"User has reached the maximum limit of {current_limit} messages",
            )
    except HTTPException:
        # Re-raise HTTPException - this is important to make sure it propagates
        raise
    except Exception as e:
        # Log other errors but don't block the message
        logger.error(f"Error checking message count for user {user_id}: {e}")

    # Create topic if it doesn't exist
    if topic_name not in topics:
        topics[topic_name] = BaseTopic(topic_name)
        logger.debug(f"Created new topic: {topic_name}")

    # Handle None metadata by defaulting to empty dict
    metadata = request.metadata if request.metadata is not None else {}

    message = Message(
        id=str(uuid.uuid4()),
        content=request.content,
        userId=user_id,
        timestamp=datetime.now(),
        metadata=metadata,
    )

    await topics[topic_name].add_message(message)
    return message


# Add a debug endpoint to list available topics
@app.get("/topics")
async def list_topics():
    """List all available topics"""
    if topics is None:
        return {"topics": []}
    return {"topics": list(topics.keys())}


# Add a debug endpoint to list messages in a topic
@app.get("/topics/{topic_name}/messages")
async def list_messages(topic_name: str):
    if topic_name not in topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    # Add await here for the async get_messages call
    messages = await topics[topic_name].get_messages(10)
    return {"messages": [msg.model_dump() for msg in messages]}


# Update the endpoint to get messages from a specific user
@app.get("/users/{user_id}/messages")
async def get_user_messages(
    user_id: str, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)
):
    """Get all messages from a specific user across all topics using efficient LanceDB filtering"""
    result = []
    total_count = 0

    # Use the optimized method for each topic
    for topic_name, topic in topics.items():
        # Get messages from this user using the efficient method
        user_messages = await topic.get_messages_by_user(
            user_id, 1000
        )  # Higher limit for aggregation
        total_count += len(user_messages)

        # Add topic information to each message
        for msg in user_messages:
            result.append(
                {
                    "message": msg.model_dump(),
                    "topic": {"name": topic_name, "description": topic.description},
                }
            )

    # Sort messages by timestamp (newest first)
    result.sort(key=lambda x: x["message"]["timestamp"], reverse=True)

    # Apply pagination
    paginated_results = result[skip : skip + limit] if skip < len(result) else []
    return {
        "user_id": user_id,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "messages": paginated_results,
    }
