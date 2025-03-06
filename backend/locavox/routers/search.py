from fastapi import APIRouter, Depends, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..services.auth_service import get_current_user_optional
from ..models.sql.user import User
from .. import config
from ..logger import setup_logger

# Create router
router = APIRouter(tags=["search"])
logger = setup_logger(__name__)


class SearchRequest(BaseModel):
    """Request model for search queries"""

    query: str
    use_llm: bool = False  # Allow client to request LLM enhancement


class SearchResponse(BaseModel):
    """Response model for search results"""

    query: str
    messages: Optional[List[Dict[str, Any]]] = None
    topic_results: Optional[List[Dict[str, Any]]] = None
    insights: Optional[str] = None
    error: Optional[str] = None


@router.post("/query", response_model=SearchResponse)
async def search_topics(
    request: SearchRequest = Body(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Enhanced search across topics with LLM-powered ranking and insights"""
    query = request.query

    # Use LLM only if explicitly requested and API key is available
    use_llm = request.use_llm and config.OPENAI_API_KEY

    # Safely access current_user.id
    user_id = "anonymous"
    if current_user is not None:
        user_id = current_user.id

    # Log the search request
    logger.info(f"Search query: '{query}' (use_llm: {use_llm}, user: {user_id})")

    try:
        # Attempt LLM-enhanced search if requested
        if use_llm:
            try:
                from ..llm_search import search_with_llm

                results = await search_with_llm(query)
                return results
            except ImportError:
                logger.warning("LLM search functionality not available")
                use_llm = False
            except Exception as e:
                logger.error(f"Error with LLM search: {str(e)}")
                use_llm = False

        # Fall back to regular search
        if not use_llm:
            from ..topic_registry import topics

            all_results = []
            for topic_name, topic in topics.items():
                messages = await topic.search_messages(query)
                if messages:
                    all_results.append(
                        {
                            "topic": topic_name,
                            "messages": [msg.model_dump() for msg in messages],
                        }
                    )

            return SearchResponse(query=query, topic_results=all_results)

    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return SearchResponse(query=query, error=f"Search failed: {str(e)}")
