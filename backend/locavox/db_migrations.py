import os
import lance
from . import config
from .logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)


async def ensure_user_id_index():
    """
    Ensure that userId field is indexed for efficient querying.
    This should be called during application startup.
    """
    try:
        database_dir = config.DATABASE_PATH
        if not os.path.exists(database_dir):
            logger.info(
                f"Database directory {database_dir} doesn't exist yet, skipping index creation"
            )
            return

        # Get all topic directories
        topic_dirs = [
            d
            for d in os.listdir(database_dir)
            if os.path.isdir(os.path.join(database_dir, d))
        ]

        for topic in topic_dirs:
            table_path = os.path.join(database_dir, topic, "messages")
            if not os.path.exists(table_path):
                continue

            # Open the Lance dataset
            ds = lance.dataset(table_path)

            # Check if index exists
            indices = ds.list_indices()
            if not any(idx["name"] == "userId_idx" for idx in indices):
                logger.info(f"Creating userId index for topic {topic}")
                # Create index on userId for efficient filtering
                ds.create_index("userId", index_name="userId_idx", index_type="flat")
                logger.info(f"Successfully created userId index for topic {topic}")

    except Exception as e:
        logger.error(f"Error ensuring userId index: {e}")


# Add more migration functions as needed
