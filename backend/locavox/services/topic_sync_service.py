import logging
from typing import Dict, Any
from ..topic_registry import register_topic, get_topic_by_id

# Set up logger for this module
logger = logging.getLogger(__name__)


class TopicRegistrySyncService:
    """
    Service for synchronizing database topics with the topic registry.
    This ensures topics from the database are available in the registry for messages.
    """

    @staticmethod
    async def sync_topic_to_registry(db_topic) -> bool:
        """
        Sync a single database topic to the registry if it doesn't already exist.

        Args:
            db_topic: The database topic object

        Returns:
            bool: True if sync was successful, False otherwise
        """
        try:
            # Check if topic is already in registry
            topic_id = str(db_topic.id)
            logger.info(f"Attempting to sync topic {topic_id} to registry")

            registry_topic = get_topic_by_id(topic_id)

            if registry_topic:
                logger.debug(f"Topic {topic_id} already exists in registry")
                return True

            logger.info(f"Topic {topic_id} not in registry, registering now")

            # Log the topic details for debugging
            logger.debug(
                f"Topic details: title={db_topic.title}, description={db_topic.description[:30]}..."
            )

            # Create a basic registry topic from the database topic
            topic_data = {
                "id": topic_id,
                "title": db_topic.title,
                "description": db_topic.description,
                "supports_messages": True,
            }

            # Register the topic in the registry
            register_topic(topic_id, topic_data)

            # Verify registration was successful
            if get_topic_by_id(topic_id):
                logger.info(f"Successfully registered topic {topic_id} in registry")
                return True
            else:
                logger.error(
                    f"Failed to register topic {topic_id} in registry - not found after registration"
                )
                return False

        except Exception as e:
            logger.error(
                f"Error syncing topic {db_topic.id} to registry: {str(e)}",
                exc_info=True,
            )
            return False

    @staticmethod
    async def sync_all_topics_to_registry(db_topics) -> Dict[str, Any]:
        """
        Sync all database topics to the registry.

        Args:
            db_topics: List of database topic objects

        Returns:
            Dict with sync statistics
        """
        results = {"total": len(db_topics), "success": 0, "failed": 0, "failed_ids": []}

        for topic in db_topics:
            success = await TopicRegistrySyncService.sync_topic_to_registry(topic)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["failed_ids"].append(str(topic.id))

        logger.info(
            f"Topic sync complete: {results['success']} synced, {results['failed']} failed"
        )
        return results
