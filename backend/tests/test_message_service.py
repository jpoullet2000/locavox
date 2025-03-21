import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import logging

from locavox.services.message_service import (
    get_message,
    delete_message,
    count_user_messages,
)
from locavox.models.schemas import Message

# Setup test logger
logger = logging.getLogger("test_message_service")


@pytest.fixture
def mock_db_connection():
    """Create a mock DB connection"""
    # Create an AsyncMock with the proper async find_one method
    db = AsyncMock()
    # Configure messages collection for MongoDB-like operations
    db.messages = AsyncMock()
    db.messages.find_one = AsyncMock()
    db.messages.delete_one = AsyncMock()
    return db


@pytest.fixture
def mock_message():
    """Create a sample message"""
    return {
        "_id": "message123",
        "topic_name": "test-topic",
        "content": "Test message content",
        "userId": "user123",
        "timestamp": "2023-01-01T12:00:00Z",
    }


@pytest.fixture
def mock_topic():
    """Create a mock topic"""
    topic = AsyncMock()
    return topic


@pytest.fixture
def mock_topic_registry(mock_topic):
    """Create a mock topic registry with multiple topics"""
    return {
        "topic1": mock_topic,
        "topic2": mock_topic,
        "topic3": mock_topic,
    }


class TestMessageService:
    """Tests for message_service module"""

    @pytest.mark.asyncio
    async def test_get_message_success(self, mock_db_connection, mock_message):
        """Test successfully getting a message by ID"""
        # Arrange
        with patch(
            "locavox.services.message_service.get_db_connection",
            return_value=mock_db_connection,
        ) as mock_get_db:
            mock_db_connection.messages.find_one.return_value = mock_message

            # We need to mock the Message class constructor to properly return a Message object
            with patch("locavox.services.message_service.Message") as MockMessage:
                # Setup the mock Message to return a message object with the right attributes
                message_instance = Mock()
                message_instance.content = mock_message["content"]
                message_instance.userId = mock_message["userId"]
                MockMessage.return_value = message_instance

                # Act
                result = await get_message("message123", "test-topic")

                # Assert
                assert result is not None
                assert result.content == mock_message["content"]
                assert result.userId == mock_message["userId"]
                mock_db_connection.messages.find_one.assert_called_once_with(
                    {"_id": "message123", "topic_name": "test-topic"}
                )
                MockMessage.assert_called_once_with(**mock_message)

    @pytest.mark.asyncio
    async def test_get_message_not_found(self, mock_db_connection):
        """Test getting a nonexistent message"""
        # Arrange
        with patch(
            "locavox.services.message_service.get_db_connection",
            return_value=mock_db_connection,
        ) as mock_get_db:
            mock_db_connection.messages.find_one.return_value = None

            # Act
            result = await get_message("nonexistent", "test-topic")

            # Assert
            assert result is None
            mock_db_connection.messages.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_message_error(self):
        """Test error handling when getting a message"""
        # Arrange
        with patch(
            "locavox.services.message_service.get_db_connection",
            side_effect=Exception("Database error"),
        ):
            # Act
            result = await get_message("message123", "test-topic")

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_message_success(self, mock_db_connection):
        """Test successfully deleting a message"""
        # Arrange
        with patch(
            "locavox.services.message_service.get_db_connection",
            return_value=mock_db_connection,
        ) as mock_get_db:
            delete_result = MagicMock()
            delete_result.deleted_count = 1
            mock_db_connection.messages.delete_one.return_value = delete_result

            # Act
            result = await delete_message("message123", "test-topic")

            # Assert
            assert result is True
            mock_db_connection.messages.delete_one.assert_called_once_with(
                {"_id": "message123", "topic_name": "test-topic"}
            )

    @pytest.mark.asyncio
    async def test_delete_message_not_found(self, mock_db_connection):
        """Test deleting a nonexistent message"""
        # Arrange
        with patch(
            "locavox.services.message_service.get_db_connection",
            return_value=mock_db_connection,
        ) as mock_get_db:
            delete_result = MagicMock()
            delete_result.deleted_count = 0
            mock_db_connection.messages.delete_one.return_value = delete_result

            # Act
            result = await delete_message("nonexistent", "test-topic")

            # Assert
            assert result is False
            mock_db_connection.messages.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_message_error(self):
        """Test error handling when deleting a message"""
        # Arrange
        with patch(
            "locavox.services.message_service.get_db_connection",
            side_effect=Exception("Database error"),
        ):
            # Act
            result = await delete_message("message123", "test-topic")

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_count_user_messages_below_limit(self, mock_topic):
        """Test counting user messages when below the limit"""
        # Arrange
        user_id = "user123"
        message_limit = 10

        # Setup topic registry
        topic_registry = {
            "topic1": mock_topic,
            "topic2": mock_topic,
            "topic3": mock_topic,
        }

        # Setup mock to return different message counts for each topic
        topic1_messages = [MagicMock(userId=user_id) for _ in range(3)]
        topic2_messages = [MagicMock(userId=user_id) for _ in range(2)]
        topic3_messages = [MagicMock(userId=user_id) for _ in range(1)]

        with patch(
            "locavox.services.message_service.get_message_limit",
            return_value=message_limit,
        ):
            with patch(
                "locavox.services.message_service.get_topics",
                return_value=topic_registry,
            ):
                # Configure the mock to return different values for different calls
                mock_topic.get_messages_by_user.side_effect = [
                    topic1_messages,
                    topic2_messages,
                    topic3_messages,
                ]

                # Act
                result = await count_user_messages(user_id)

                # Assert
                assert result == 6  # 3 + 2 + 1
                assert mock_topic.get_messages_by_user.call_count == 3
                # Verify the manual count wasn't triggered
                mock_topic.get_messages.assert_not_called()

    @pytest.mark.asyncio
    @patch("locavox.services.message_service.get_topics")
    @patch("locavox.services.message_service.get_message_limit")
    async def test_count_user_messages_at_limit(
        self, mock_get_limit, mock_get_topics, mock_topic_registry, mock_topic
    ):
        """Test counting user messages when at the limit"""
        # Arrange
        user_id = "user123"
        message_limit = 10
        mock_get_limit.return_value = message_limit
        mock_get_topics.return_value = mock_topic_registry

        # Setup mock to return messages at the limit
        topic1_messages = [MagicMock(userId=user_id) for _ in range(5)]
        topic2_messages = [MagicMock(userId=user_id) for _ in range(5)]  # Total: 10
        topic3_messages = []  # No need to process this

        mock_topic.get_messages_by_user.side_effect = [
            topic1_messages,
            topic2_messages,
            topic3_messages,
        ]

        # Act
        result = await count_user_messages(user_id)

        # Assert
        assert result == 10
        assert (
            mock_topic.get_messages_by_user.call_count == 2
        )  # Early return after reaching limit
        # Verify we didn't call get_messages (manual verification)
        mock_topic.get_messages.assert_not_called()

    @pytest.mark.asyncio
    @patch("locavox.services.message_service.get_topics")
    @patch("locavox.services.message_service.get_message_limit")
    async def test_count_user_messages_near_limit_triggers_verification(
        self, mock_get_limit, mock_get_topics, mock_topic_registry, mock_topic
    ):
        """Test that being near the limit triggers manual verification"""
        # Arrange
        user_id = "user123"
        message_limit = 10
        mock_get_limit.return_value = message_limit
        mock_get_topics.return_value = mock_topic_registry

        # Setup counts to be just under the limit to trigger verification
        topic1_messages = [MagicMock(userId=user_id) for _ in range(4)]
        topic2_messages = [MagicMock(userId=user_id) for _ in range(4)]
        topic3_messages = [MagicMock(userId=user_id) for _ in range(1)]  # Total: 9

        mock_topic.get_messages_by_user.side_effect = [
            topic1_messages,
            topic2_messages,
            topic3_messages,
        ]

        # Setup manual verification - we need 5 messages for each topic to match the implementation
        # 5 messages * 3 topics = 15 total, but since we're filtering by user_id,
        # we need each topic to return some of the user's messages
        all_messages = [
            MagicMock(userId=user_id if i < 2 else "other_user")
            for i in range(5)  # Only 2 per topic will belong to user_id
        ]

        # We need to ensure we don't exceed the limit with manual verification
        # Each topic will have 2 messages for our user, making a total of 6
        # which is less than 9, so the original count will stand
        mock_topic.get_messages.return_value = all_messages

        # Act
        result = await count_user_messages(user_id)

        # Assert
        assert result == 9  # Original count should be used
        assert mock_topic.get_messages_by_user.call_count == 3
        # Verify we called get_messages for manual verification
        assert mock_topic.get_messages.call_count == 3

    @pytest.mark.asyncio
    @patch("locavox.services.message_service.get_topics")
    @patch("locavox.services.message_service.get_message_limit")
    async def test_count_user_messages_with_test_limit(
        self, mock_get_limit, mock_get_topics, mock_topic_registry, mock_topic
    ):
        """Test counting messages with a test limit override"""
        # Arrange
        user_id = "user123"
        test_limit = 5  # Override default limit
        mock_get_topics.return_value = mock_topic_registry

        # Mock responses
        topic1_messages = [MagicMock(userId=user_id) for _ in range(3)]
        topic2_messages = [
            MagicMock(userId=user_id) for _ in range(3)
        ]  # Total: 6 > test_limit

        mock_topic.get_messages_by_user.side_effect = [
            topic1_messages,
            topic2_messages,
        ]

        # Act
        result = await count_user_messages(user_id, test_limit)

        # Assert
        assert result == 6
        assert mock_topic.get_messages_by_user.call_count == 2
        # Verify get_message_limit wasn't called due to override
        mock_get_limit.assert_not_called()

    @pytest.mark.asyncio
    @patch("locavox.services.message_service.get_topics")
    @patch("locavox.services.message_service.get_message_limit")
    async def test_count_user_messages_with_error_in_topic(
        self, mock_get_limit, mock_get_topics, mock_topic_registry, mock_topic
    ):
        """Test error handling within a specific topic"""
        # Arrange
        user_id = "user123"
        message_limit = 10
        mock_get_limit.return_value = message_limit
        mock_get_topics.return_value = mock_topic_registry

        # First topic works fine
        topic1_messages = [MagicMock(userId=user_id) for _ in range(3)]
        # Second topic raises an exception
        error_exception = Exception("Topic error")
        # Third topic works fine
        topic3_messages = [MagicMock(userId=user_id) for _ in range(2)]

        mock_topic.get_messages_by_user.side_effect = [
            topic1_messages,
            error_exception,
            topic3_messages,
        ]

        # Act
        result = await count_user_messages(user_id)

        # Assert
        assert result == 5  # 3 + 0 + 2
        assert mock_topic.get_messages_by_user.call_count == 3


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
