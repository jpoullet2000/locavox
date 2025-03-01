import pytest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from locavox.main import app
from locavox.models import Message, Topic, CommunityTaskMarketplace, NeighborhoodHubChat

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
async def setup_test_topics(event_loop):
    """Setup test topics with messages from different users"""
    # Reset topics for each test
    from locavox.main import topics

    # Create clean test topics
    topics.clear()
    topics["marketplace"] = CommunityTaskMarketplace()
    topics["chat"] = NeighborhoodHubChat()
    topics["test_topic"] = Topic("test_topic")

    # Create test users
    user1_id = "test_user_1"
    user2_id = "test_user_2"

    # Add messages from user1 to marketplace
    for i in range(5):
        message = Message(
            id=str(uuid.uuid4()),
            userId=user1_id,
            content=f"User1 marketplace message {i}",
            timestamp=datetime.now() - timedelta(hours=i),
            metadata={"test": True, "index": i},
        )
        await topics["marketplace"].add_message(message)

    # Add messages from user2 to marketplace
    for i in range(3):
        message = Message(
            id=str(uuid.uuid4()),
            userId=user2_id,
            content=f"User2 marketplace message {i}",
            timestamp=datetime.now() - timedelta(hours=i + 1),
            metadata={"test": True, "index": i},
        )
        await topics["marketplace"].add_message(message)

    # Add messages from user1 to chat
    for i in range(4):
        message = Message(
            id=str(uuid.uuid4()),
            userId=user1_id,
            content=f"User1 chat message {i}",
            timestamp=datetime.now() - timedelta(hours=i + 2),
            metadata={"test": True, "index": i},
        )
        await topics["chat"].add_message(message)

    # Add messages from user2 to test_topic
    for i in range(7):
        message = Message(
            id=str(uuid.uuid4()),
            userId=user2_id,
            content=f"User2 test_topic message {i}",
            timestamp=datetime.now() - timedelta(hours=i),
            metadata={"test": True, "index": i},
        )
        await topics["test_topic"].add_message(message)


@pytest.mark.asyncio
async def test_get_user_messages():
    """Test retrieving messages from a specific user"""
    # Test for user1 who has messages in multiple topics
    response = client.get("/users/test_user_1/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == "test_user_1"
    assert data["total"] == 9  # 5 from marketplace + 4 from chat
    assert len(data["messages"]) == 9

    # Verify messages are sorted by timestamp (newest first)
    timestamps = [msg["message"]["timestamp"] for msg in data["messages"]]
    assert timestamps == sorted(timestamps, reverse=True)

    # Verify topic information is included
    topics_found = {msg["topic"]["name"] for msg in data["messages"]}
    assert "marketplace" in topics_found
    assert "chat" in topics_found
    assert "test_topic" not in topics_found  # User1 has no messages here


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
