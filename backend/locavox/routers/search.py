from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from ..services import auth_service
from ..models.user import User
from ..logger import setup_logger
from ..topic_registry import get_topics
from .. import config  # Import config directly

# Set up logger for this module
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)

# Get references to topics from a central store
topics = get_topics()


class QueryRequest(BaseModel):
    query: str
    use_llm: bool = config.USE_LLM_BY_DEFAULT  # Use config directly


@router.post("")
async def query_topics(
    request: QueryRequest,
    current_user: Optional[User] = Depends(auth_service.get_current_user_optional),
):
    """Enhanced search across topics with LLM-powered ranking and insights"""
    query = request.query

    # Use LLM only if explicitly requested and API key is available
    use_llm = request.use_llm and config.OPENAI_API_KEY

    # Log the search request
    logger.info(
        f"Search query: '{query}' (use_llm: {use_llm}, user: {current_user.id if current_user else 'anonymous'})"
    )

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
            from ..llm_search import SmartSearch

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
