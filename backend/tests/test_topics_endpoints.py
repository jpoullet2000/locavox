import pytest
from fastapi.testclient import TestClient
from locavox.main import app  # Updated import path
from locavox.services import message_service, auth_service  # Updated import path
from unittest.mock import patch, MagicMock
from locavox.models.user import User
import logging

# Set up a logger for this test module
logger = logging.getLogger("test_topics_endpoints")

# Create a test client
client = TestClient(app)


def get_test_user_override():
    """Override dependency for get_current_user in tests"""
    # Return a User object directly (not an async function)
    return User(
        id="test_user_id",
        username="testuser",
        email="test@example.com",
        is_active=True,
    )


def setup_auth_override():
    """Set up the app to override the auth dependency for a test"""
    # Store original dependency
    original_dependency = app.dependency_overrides.copy()

    # Override the auth dependency
    app.dependency_overrides[auth_service.get_current_user] = get_test_user_override

    # Return a cleanup function
    def cleanup():
        app.dependency_overrides = original_dependency

    return cleanup


@pytest.mark.asyncio
async def test_delete_message_success():
    """Test that authorized users can delete their own messages"""
    # Create a mock for the message that "belongs" to our test user
    message_mock = MagicMock()
    message_mock.user_id = "test_user_id"  # Match the ID in get_test_user_override

    # Set up dependency overrides for auth
    cleanup = setup_auth_override()

    try:
        # Mock the message service methods
        with patch.object(message_service, "get_message", return_value=message_mock):
            with patch.object(message_service, "delete_message", return_value=True):
                # Make the request
                response = client.delete("/topics/test_topic/messages/test_message_id")

                # Check the status code
                assert response.status_code == 204, (
                    f"Expected 204, got {response.status_code}"
                )
    finally:
        # Clean up the overrides
        cleanup()


@pytest.mark.asyncio
async def test_delete_message_not_found():
    """Test that deleting a non-existent message returns 404"""
    # Set up dependency overrides for auth
    cleanup = setup_auth_override()

    try:
        # Mock get_message to return None (message not found)
        with patch.object(message_service, "get_message", return_value=None):
            response = client.delete("/topics/test_topic/messages/non_existent_id")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
    finally:
        # Clean up the overrides
        cleanup()


@pytest.mark.asyncio
async def test_delete_message_forbidden():
    """Test that users cannot delete messages from other users"""
    # Create a mock message with different owner
    message_mock = MagicMock()
    message_mock.user_id = "different_user_id"  # Different from test_user_id

    # Set up dependency overrides for auth
    cleanup = setup_auth_override()

    try:
        # Mock get_message to return a message owned by a different user
        with patch.object(message_service, "get_message", return_value=message_mock):
            response = client.delete("/topics/test_topic/messages/test_message_id")

            assert response.status_code == 403
            assert "only delete your own messages" in response.json()["detail"].lower()
    finally:
        # Clean up the overrides
        cleanup()


# Add some additional tests to verify the message-related endpoints


@pytest.mark.asyncio
async def test_list_messages():
    """Test listing messages in a topic"""
    # Mock the topic registry get function to return a mock topic
    from locavox.topic_registry import topics

    # Create a test topic and add it to the registry
    from locavox.models import BaseTopic, Message
    from datetime import datetime

    # Store original topics and clear for test
    original_topics = topics.copy()
    topics.clear()

    try:
        # Create a test topic
        test_topic = BaseTopic("test_topic")
        topics["test_topic"] = test_topic

        # Add a test message to the topic
        test_message = Message(
            id="test_id",
            content="Test message content",
            userId="test_user_id",
            timestamp=datetime.now(),
        )
        await test_topic.add_message(test_message)

        # Make the request
        response = client.get("/topics/test_topic/messages")

        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 1
        assert data["messages"][0]["id"] == "test_id"
    finally:
        # Restore original topics registry
        topics.clear()
        for k, v in original_topics.items():
            topics[k] = v
