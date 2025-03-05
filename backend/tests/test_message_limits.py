import pytest
from fastapi.testclient import TestClient
from locavox.main import app
from locavox.models import BaseTopic
from locavox import config
from locavox.logger import setup_logger


# Set up logger for tests
logger = setup_logger("tests.message_limits")


# Make sure we get a fresh client for each test
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_limit():
    """Fixture that returns the test-specific message limit"""
    return 5  # Fixed test limit


@pytest.fixture(autouse=True)
async def setup_test_environment(event_loop, test_limit):
    """Setup test environment with a clean topic"""
    # Import the topic registry directly
    from locavox.topic_registry import topics
    from locavox.config_helpers import set_test_value, reset_test_values

    # Store original limit value
    original_limit = config.MAX_MESSAGES_PER_USER

    try:
        # Set a smaller limit for testing using config_helpers
        set_test_value("MAX_MESSAGES_PER_USER", test_limit)

        # Also update the regular config (for functions that might still access it directly)
        config.MAX_MESSAGES_PER_USER = test_limit

        logger.info(f"Test limit set to {test_limit} messages per user")

        # Create clean test topics - clear the dictionary
        topics.clear()
        topics["test_topic"] = BaseTopic("test_topic")

        # Verify the limit was set correctly in both places
        from locavox.config_helpers import get_message_limit

        actual_limit = get_message_limit()
        assert actual_limit == test_limit, (
            f"Expected test limit to be {test_limit}, but got {actual_limit}"
        )
        assert config.MAX_MESSAGES_PER_USER == test_limit, (
            f"Config not updated, expected {test_limit}, got {config.MAX_MESSAGES_PER_USER}"
        )

        yield
    finally:
        # Always restore original limit and reset test values
        config.MAX_MESSAGES_PER_USER = original_limit
        reset_test_values()


# Update all test functions to use the client fixture
@pytest.mark.asyncio
async def test_message_limit_enforcement(client, test_limit):
    """Test that users cannot exceed the message limit"""
    user_id = "limit_test_user"

    # Log what we're testing with
    logger.info(f"Testing with explicit limit: {test_limit}")

    # Verify the initial count is zero
    response = client.get(f"/users/{user_id}/messages")
    assert response.status_code == 200
    initial_count = response.json()["total"]
    assert initial_count == 0, f"Expected 0 initial messages, found {initial_count}"

    # Add messages up to the limit - pass test_limit as a query parameter
    for i in range(test_limit):
        response = client.post(
            f"/topics/test_topic/messages?test_limit={test_limit}",
            json={
                "userId": user_id,
                "content": f"Test message {i}",
                "metadata": {"test": True, "test_index": i},
            },
        )
        assert response.status_code == 200, (
            f"Failed to add message {i}: {response.text}"
        )

    # Try to add one more message - should fail
    # Make sure to include the test_limit parameter
    extra_msg = {
        "userId": user_id,
        "content": "This message should be rejected",
        "metadata": {"test": True, "should_fail": True},
    }

    logger.info("About to post message that should exceed limit...")
    response = client.post(
        f"/topics/test_topic/messages?test_limit={test_limit}", json=extra_msg
    )

    # Log the response for debugging
    logger.info(f"Got response {response.status_code} - {response.text}")

    # This should now correctly assert
    assert response.status_code == 429, "Should return 429 Too Many Requests"
    assert "maximum limit" in response.json()["detail"]


# Also update the other test functions to use the test_limit parameter
@pytest.mark.asyncio
async def test_different_users_separate_limits(client, test_limit):
    """Test that different users have separate message limits"""
    user1_id = "limit_test_user_1"
    user2_id = "limit_test_user_2"

    # Add messages up to the limit for user1
    for i in range(test_limit):
        response = client.post(
            f"/topics/test_topic/messages?test_limit={test_limit}",
            json={
                "userId": user1_id,
                "content": f"User1 message {i}",
                "metadata": {"test": True},
            },
        )
        assert response.status_code == 200

    # User1 should be at limit
    response = client.post(
        f"/topics/test_topic/messages?test_limit={test_limit}",
        json={
            "userId": user1_id,
            "content": "This message should be rejected",
        },
    )
    assert response.status_code == 429

    # User2 should still be able to add messages
    for i in range(test_limit):
        response = client.post(
            f"/topics/test_topic/messages?test_limit={test_limit}",
            json={
                "userId": user2_id,
                "content": f"User2 message {i}",
                "metadata": {"test": True},
            },
        )
        assert response.status_code == 200, f"User2 should be able to add message {i}"

    # Now user2 should also be at limit
    response = client.post(
        f"/topics/test_topic/messages?test_limit={test_limit}",
        json={
            "userId": user2_id,
            "content": "This message should be rejected",
        },
    )
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_messages_across_topics_count_toward_limit(client, test_limit):
    """Test that messages across different topics count toward the same user limit"""
    user_id = "multi_topic_user"

    # Add messages to different topics
    topics_list = ["topic1", "topic2", "topic3"]

    # Add messages across multiple topics up to the limit
    for i in range(test_limit):
        topic = topics_list[i % len(topics_list)]
        response = client.post(
            f"/topics/{topic}/messages?test_limit={test_limit}",
            json={
                "userId": user_id,
                "content": f"Message {i} in {topic}",
            },
        )
        assert response.status_code == 200

    # Next message should fail regardless of topic
    response = client.post(
        f"/topics/{topics_list[0]}/messages?test_limit={test_limit}",
        json={
            "userId": user_id,
            "content": "This should fail",
        },
    )
    assert response.status_code == 429

    # Check count across all topics
    response = client.get(f"/users/{user_id}/messages")
    data = response.json()
    assert data["total"] == test_limit


@pytest.mark.asyncio
async def test_message_limits_on_base_topic_subclasses(client, test_limit):
    """Test message limit enforcement on BaseTopic subclasses"""
    # Import the topics registry directly
    from locavox.topic_registry import topics
    from locavox.models import MarketplaceTopic

    # Create a user and topic
    user_id = "base_topic_user"

    # Use the MarketplaceTopic class which is a BaseTopic subclass
    # Clear the existing topics first
    topics.clear()
    topics["marketplace"] = MarketplaceTopic()

    # Add messages up to the limit
    for i in range(test_limit):
        response = client.post(
            f"/topics/marketplace/messages?test_limit={test_limit}",
            json={
                "userId": user_id,
                "content": f"Base topic message {i}",
            },
        )
        assert response.status_code == 200

    # Try to add one more message - should fail
    response = client.post(
        f"/topics/marketplace/messages?test_limit={test_limit}",
        json={
            "userId": user_id,
            "content": "This message should be rejected",
        },
    )
    assert response.status_code == 429

    # Verify we can retrieve messages using the user endpoint
    response = client.get(f"/users/{user_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == test_limit
