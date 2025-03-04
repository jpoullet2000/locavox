import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from locavox.main import app
from locavox.models import Message, BaseTopic
from locavox.logger import setup_logger
from locavox.topic_registry import topics

# Setup logger
logger = setup_logger("tests.user_endpoints")

# Create a test client
client = TestClient(app)


@pytest.fixture(scope="module")
async def setup_test_topics():
    """Setup test topics and return status"""
    logger.info("Setting up test topics and messages")

    # Store original topics
    original_topics = dict(topics)

    try:
        # Clear and recreate topics
        topics.clear()
        topics["marketplace"] = BaseTopic(name="marketplace")
        topics["chat"] = BaseTopic(name="chat")
        topics["test_topic"] = BaseTopic(name="test_topic")

        logger.info(f"Created topics: {list(topics.keys())}")

        # Define test users
        user1_id = "test_user_1"
        user2_id = "test_user_2"

        # Add messages for user1
        for i in range(5):
            await topics["marketplace"].add_message(
                Message(
                    id=f"user1-marketplace-{i}",
                    userId=user1_id,
                    content=f"User1 marketplace message {i}",
                    timestamp=datetime.now() - timedelta(hours=i),
                    metadata={"test": True, "index": i},
                )
            )

        for i in range(4):
            await topics["chat"].add_message(
                Message(
                    id=f"user1-chat-{i}",
                    userId=user1_id,
                    content=f"User1 chat message {i}",
                    timestamp=datetime.now() - timedelta(hours=i + 2),
                    metadata={"test": True, "index": i},
                )
            )

        # Add messages for user2
        for i in range(3):
            await topics["marketplace"].add_message(
                Message(
                    id=f"user2-marketplace-{i}",
                    userId=user2_id,
                    content=f"User2 marketplace message {i}",
                    timestamp=datetime.now() - timedelta(hours=i + 1),
                    metadata={"test": True, "index": i},
                )
            )

        for i in range(7):
            await topics["test_topic"].add_message(
                Message(
                    id=f"user2-test-{i}",
                    userId=user2_id,
                    content=f"User2 test_topic message {i}",
                    timestamp=datetime.now() - timedelta(hours=i),
                    metadata={"test": True, "index": i},
                )
            )

        # Verify setup
        user1_messages = len(
            await topics["marketplace"].get_messages_by_user(user1_id)
        ) + len(await topics["chat"].get_messages_by_user(user1_id))

        assert user1_messages == 9, (
            f"Expected 9 messages for user1, found {user1_messages}"
        )

        yield {
            "success": True,
            "user1_id": user1_id,
            "user2_id": user2_id,
            "topics": list(topics.keys()),
        }

    except Exception as e:
        logger.error(f"Error in test setup: {e}")
        yield {"success": False, "error": str(e)}

    finally:
        # Cleanup - restore original topics
        topics.clear()
        topics.update(original_topics)
        logger.info("Restored original topics")


@pytest.mark.skip("Skipping test for now")
@pytest.mark.asyncio
async def test_get_user_messages(setup_test_topics):
    """Test retrieving messages from a specific user"""
    assert setup_test_topics["success"], (
        f"Test setup failed: {setup_test_topics.get('error')}"
    )

    user1_id = setup_test_topics["user1_id"]
    response = client.get(f"/users/{user1_id}/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user1_id
    assert data["total"] == 9
    assert len(data["messages"]) == 9

    # Verify topic information
    topics_found = {msg["topic"]["name"] for msg in data["messages"]}
    assert "marketplace" in topics_found
    assert "chat" in topics_found
    assert "test_topic" not in topics_found


@pytest.mark.skip("Skipping test for now")
@pytest.mark.asyncio
async def test_get_user_messages_pagination():
    """Test pagination for user messages endpoint"""
    # Test for user2 with pagination
    response = client.get("/users/test_user_2/messages?skip=2&limit=3")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == "test_user_2"
    assert data["total"] == 10  # 3 from marketplace + 7 from test_topic
    assert data["skip"] == 2
    assert data["limit"] == 3
    assert len(data["messages"]) == 3  # Limited to 3 items

    # Get another page
    response = client.get("/users/test_user_2/messages?skip=5&limit=5")
    assert response.status_code == 200

    data = response.json()
    assert len(data["messages"]) == 5
    assert data["total"] == 10


@pytest.mark.asyncio
async def test_get_user_messages_nonexistent_user():
    """Test behavior when user doesn't exist"""
    response = client.get("/users/nonexistent_user/messages")
    assert response.status_code == 200  # Should return success with empty results

    data = response.json()
    assert data["user_id"] == "nonexistent_user"
    assert data["total"] == 0
    assert len(data["messages"]) == 0


@pytest.mark.asyncio
async def test_user_messages_content_verification():
    """Verify the content of returned messages"""
    response = client.get("/users/test_user_1/messages?limit=5")
    assert response.status_code == 200

    data = response.json()
    messages = data["messages"]

    # Verify message content contains expected substring
    for msg in messages:
        assert "User1" in msg["message"]["content"]
        assert msg["message"]["userId"] == "test_user_1"

        # Verify metadata is preserved
        assert "test" in msg["message"]["metadata"]
        assert msg["message"]["metadata"]["test"] is True


@pytest.mark.asyncio
async def test_add_and_retrieve_user_message():
    """Test adding a new message and then retrieving it through the user endpoint"""
    # Add a new message
    new_message = {
        "userId": "test_user_3",
        "content": "This is a test message from user 3",
        "metadata": {"source": "test", "priority": "high"},
    }

    response = client.post("/topics/new_topic/messages", json=new_message)
    assert response.status_code == 200

    # Now retrieve it via user endpoint
    response = client.get("/users/test_user_3/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["messages"][0]["message"]["content"] == new_message["content"]
    assert data["messages"][0]["topic"]["name"] == "new_topic"
    assert data["messages"][0]["message"]["metadata"]["priority"] == "high"
