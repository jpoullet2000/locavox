from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.user import User
from ..services import auth_service
from ..logger import setup_logger
from ..topic_registry import get_topics

# Set up logger for this module
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Get references to topics from a central store
topics = get_topics()


@router.get("/{user_id}/messages")
async def get_user_messages(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(auth_service.get_current_user_optional),
):
    """Get all messages from a specific user across all topics using efficient LanceDB filtering"""
    # Optional authorization check - if user is authenticated, they can only see their own messages
    # unless they have admin privileges
    if (
        current_user is not None
        and current_user.id != user_id
        and not current_user.is_admin
    ):
        logger.warning(
            f"User {current_user.id} tried to access messages of user {user_id}"
        )
        raise HTTPException(
            status_code=403, detail="You can only view your own messages"
        )

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
