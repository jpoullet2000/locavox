from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from ..models.sql.user import User as UserModel  # Import SQLAlchemy model
from ..models.schemas.user import UserCreate, UserResponse  # Import Pydantic schemas
from ..services.auth_service import get_current_user_optional, get_current_user
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


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get a list of users with pagination.

    This endpoint requires authentication.
    Only active users will be returned.
    Results are sorted by creation date (newest first).
    """
    logger.info(f"Getting users with skip={skip}, limit={limit}")

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can see users")

    try:
        # Query to get users with pagination - FIX: Changed 'is True' to '== True'
        stmt = (
            select(UserModel)
            .where(UserModel.is_active == True)  # noqa
            .order_by(UserModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        users = result.scalars().all()

        logger.info(f"Found {len(users)} users")
        return users

    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving users",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),  # Require authentication
):
    """
    Get a specific user by ID.

    This endpoint requires authentication.
    Users can only view their own profile unless they are admins.
    """
    logger.info(f"Getting user with id {user_id}")

    try:
        # Check if the user is requesting their own profile or is an admin
        if user_id != current_user.id and not current_user.is_superuser:
            logger.warning(
                f"User {current_user.id} tried to access profile of user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile unless you are an admin",
            )

        # Get user from database - FIX: Changed 'is True' to '== True'
        stmt = select(UserModel).where(
            (UserModel.id == user_id) & (UserModel.is_active == True)  # noqa
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"User with id {user_id} not found or not active")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user",
        )


@router.get("/{user_id}/messages")
async def get_user_messages(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
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
            # Check if topic supports get_messages_by_user method
            if hasattr(topic, "get_messages_by_user"):
                logger.debug(f"Topic {topic_name} has get_messages_by_user method")
                # Get messages by this user in this topic
                user_messages = await topic.get_messages_by_user(user_id)
                logger.debug(
                    f"Found {len(user_messages)} messages from user {user_id} in topic {topic_name}"
                )
            else:
                # Fallback: get all messages and filter by user_id
                logger.debug(
                    f"Topic {topic_name} doesn't have get_messages_by_user method, using fallback"
                )

                # Check if the topic has a get_messages method
                if hasattr(topic, "get_messages"):
                    # Get all messages and filter - use a large limit instead of None
                    try:
                        # Use a large but finite limit (1000) instead of None
                        all_topic_messages = await topic.get_messages(
                            skip=0, limit=1000
                        )
                        # Filter messages by user_id
                        user_messages = [
                            msg
                            for msg in all_topic_messages
                            if msg.get("user_id") == user_id
                        ]
                        logger.debug(
                            f"Found {len(user_messages)} messages from user {user_id} in topic {topic_name} using fallback"
                        )
                    except TypeError as e:
                        logger.error(f"TypeError using get_messages: {e}")
                        # Try with a different limit if None causes an issue
                        all_topic_messages = await topic.get_messages(skip=0, limit=100)
                        user_messages = [
                            msg
                            for msg in all_topic_messages
                            if msg.get("user_id") == user_id
                        ]
                else:
                    logger.warning(
                        f"Topic {topic_name} doesn't support either get_messages_by_user or get_messages"
                    )
                    continue

            # Build response with message and topic info
            for message in user_messages:
                all_messages.append(
                    {
                        "message": message.model_dump()
                        if hasattr(message, "model_dump")
                        else message,
                        "topic": {
                            "name": topic_name,
                            "description": getattr(topic, "description", topic_name),
                            "id": getattr(topic, "id", topic_name),  # Include topic ID
                        },
                    }
                )
        except Exception as e:
            # Log the error but continue with other topics
            logger.error(
                f"Error getting messages for user {user_id} in topic {topic_name}: {e}"
            )
            # Print full exception with traceback for debugging
            import traceback

            logger.error(f"Exception traceback: {traceback.format_exc()}")

    # Make sure we can properly sort the messages
    for msg in all_messages:
        if isinstance(msg["message"], dict) and "timestamp" not in msg["message"]:
            # If timestamp is missing, add a default one (current time) to avoid sorting errors
            msg["message"]["timestamp"] = datetime.now().isoformat()

    # Sort all messages by timestamp (newest first)
    try:
        all_messages.sort(key=lambda x: x["message"]["timestamp"], reverse=True)
    except (KeyError, TypeError) as e:
        logger.error(f"Error sorting messages: {e}")
        # If sorting fails, at least return the unsorted messages

    # Apply pagination
    paginated_messages = all_messages[skip : skip + limit]
    total_count = len(all_messages)

    logger.info(f"Found {total_count} total messages for user {user_id}")

    # Log message IDs for debugging
    if total_count > 0:
        message_ids = [msg["message"].get("id") for msg in all_messages]
        logger.info(f"Message IDs found: {message_ids}")
    else:
        logger.warning(f"No messages found for user {user_id}")

    # Return paginated results
    return {
        "user_id": user_id,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "messages": paginated_messages,
    }
