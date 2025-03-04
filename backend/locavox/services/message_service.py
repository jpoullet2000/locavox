from typing import Optional
from ..models import Message  # Updated import
from ..db.database import get_db_connection
import logging
from ..config_helpers import get_message_limit
from ..topic_registry import get_topics

logger = logging.getLogger(__name__)


async def get_message(message_id: str, topic_name: str) -> Optional[Message]:
    """
    Get a specific message by ID from a topic.
    """
    try:
        db = await get_db_connection()
        message_data = await db.messages.find_one(
            {"_id": message_id, "topic_name": topic_name}
        )

        if not message_data:
            return None

        return Message(**message_data)
    except Exception as e:
        logger.error(
            f"Error retrieving message {message_id} from topic {topic_name}: {str(e)}"
        )
        return None


async def delete_message(message_id: str, topic_name: str) -> bool:
    """
    Delete a message from a topic.

    Returns True if deletion was successful, False otherwise.
    """
    try:
        db = await get_db_connection()
        result = await db.messages.delete_one(
            {"_id": message_id, "topic_name": topic_name}
        )

        # Check if message was actually deleted
        if result.deleted_count == 0:
            logger.warning(
                f"No message with id {message_id} found in topic {topic_name} to delete"
            )
            return False

        logger.info(
            f"Successfully deleted message {message_id} from topic {topic_name}"
        )
        return True
    except Exception as e:
        logger.error(
            f"Error deleting message {message_id} from topic {topic_name}: {str(e)}"
        )
        return False


async def count_user_messages(user_id: str, test_limit: Optional[int] = None) -> int:
    """Count the total number of messages from a user across all topics"""
    total_count = 0
    logger.debug(f"Counting messages for user {user_id}")

    # Get topics from registry
    topics = get_topics()

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
