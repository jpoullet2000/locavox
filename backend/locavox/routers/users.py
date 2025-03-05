from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.sql.user import User as UserModel  # Import SQLAlchemy model
from ..models.schemas.user import UserCreate, UserResponse  # Import Pydantic schemas
from ..services.auth_service import get_current_user_optional
from ..topic_registry import topics
from ..logger import setup_logger
from locavox.database import get_db_session  # Change to get_db_session
from locavox.services.user_service import create_user, UserExistsError

# Create logger for this module
logger = setup_logger(__name__)

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/{user_id}/messages")
async def get_user_messages(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    """
    Get messages posted by a specific user across all topics.

    Results are returned in reverse chronological order (newest first).
    """
    logger.info(f"Getting messages for user {user_id}")

    # Collect messages from all topics
    all_messages = []
    all_topics = topics

    # Log the topics we're checking
    logger.info(f"Checking {len(all_topics)} topics: {list(all_topics.keys())}")

    for topic_name, topic in all_topics.items():
        try:
            # Get messages by this user in this topic
            user_messages = await topic.get_messages_by_user(user_id)
            logger.debug(
                f"Found {len(user_messages)} messages from user {user_id} in topic {topic_name}"
            )

            # Build response with message and topic info
            for message in user_messages:
                all_messages.append(
                    {
                        "message": message.model_dump(),
                        "topic": {
                            "name": topic_name,
                            "description": getattr(topic, "description", topic_name),
                        },
                    }
                )
        except Exception as e:
            # Log the error but continue with other topics
            logger.error(
                f"Error getting messages for user {user_id} in topic {topic_name}: {e}"
            )

    # Sort all messages by timestamp (newest first)
    all_messages.sort(key=lambda x: x["message"]["timestamp"], reverse=True)

    # Apply pagination
    paginated_messages = all_messages[skip : skip + limit]
    total_count = len(all_messages)

    logger.info(f"Found {total_count} total messages for user {user_id}")

    # Return paginated results
    return {
        "user_id": user_id,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "messages": paginated_messages,
    }


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),  # Change to get_db_session
):
    """
    Create a new user
    """
    try:
        user = await create_user(db, user_data)
        return user
    except UserExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
