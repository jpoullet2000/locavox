"""
Database connection module.
This is a simplified version for demonstration purposes.
"""

from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class MockDB:
    """Mock database class for demonstration purposes"""

    def __init__(self):
        self.messages = MockCollection("messages")
        self.users = MockCollection("users")

    async def close(self):
        """Close the database connection"""
        logger.info("Closing database connection")


class MockCollection:
    """Mock database collection for demonstration purposes"""

    def __init__(self, name: str):
        self.name = name
        self._data = {}

    async def find_one(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Find a single document matching the filter"""
        for doc_id, doc in self._data.items():
            match = True
            for k, v in filter_dict.items():
                if k not in doc or doc[k] != v:
                    match = False
                    break
            if match:
                return doc
        return None

    async def delete_one(self, filter_dict: Dict[str, Any]) -> Dict[str, int]:
        """Delete a single document matching the filter"""
        for doc_id, doc in list(
            self._data.items()
        ):  # Use list to avoid modification during iteration
            match = True
            for k, v in filter_dict.items():
                if k not in doc or doc[k] != v:
                    match = False
                    break
            if match:
                del self._data[doc_id]
                return {"deleted_count": 1}
        return {"deleted_count": 0}


# Database instance
_db = None


async def get_db_connection():
    """Get a database connection"""
    global _db
    if _db is None:
        _db = MockDB()
    return _db
