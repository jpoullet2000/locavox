import pytest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from locavox.main import app
from locavox.models import Message, BaseTopic
from locavox.logger import setup_logger

# Set up logger for tests
logger = setup_logger("tests.user_messages")

# Create a test client
client = TestClient(app)


@pytest.fixture
async def setup_test_data(event_loop):
    """Setup test data for user messages endpoint tests"""
    # Import the topics in a way that ensures we get the dictionary
    from locavox.topic_registry import topics

    # Create test users
    user_ids = [f"test_user_{i}" for i in range(3)]

    # Create test topics
    topic_names = ["topic_a", "topic_b", "topic_c"]

    # Clear existing topics - make sure we're working with a clean slate
    try:
        topics.clear()
    except (AttributeError, TypeError) as e:
        # If topics isn't a dictionary, try accessing it differently
        logger.warning(f"Could not clear topics: {e}")
        # Fallback approach - try importing get_topics function
        try:
            from locavox.topic_registry import get_topics

            topic_dict = get_topics()
            topic_dict.clear()
            # Update the module-level reference
            globals()["topics"] = topic_dict
        except Exception as e:
            logger.error(f"Failed to clear topics registry: {e}")
            raise

    # Verify topics is a dictionary - if not, raise a clear error
    if not isinstance(topics, dict):
        raise TypeError(f"Expected topics to be a dict, but got {type(topics)}")

    # Create fresh topics
    for name in topic_names:
        topics[name] = BaseTopic(name)

    # Add messages with timestamps in descending order for chronological testing
    now = datetime.now()

    # Add 5 messages from user_0 to topic_a
    for i in range(5):
        msg = Message(
            id=str(uuid.uuid4()),
            userId=user_ids[0],
            content=f"User 0 message {i} in topic A",
            timestamp=now - timedelta(minutes=i),
            metadata={"index": i, "topic": "topic_a"},
        )
        await topics["topic_a"].add_message(msg)

    # Add 3 messages from user_0 to topic_b
    for i in range(3):
        msg = Message(
            id=str(uuid.uuid4()),
            userId=user_ids[0],
            content=f"User 0 message {i} in topic B",
            timestamp=now - timedelta(minutes=i + 5),
            metadata={"index": i, "topic": "topic_b"},
        )
        await topics["topic_b"].add_message(msg)

    # Add 4 messages from user_1 to topic_b
    for i in range(4):
        msg = Message(
            id=str(uuid.uuid4()),
            userId=user_ids[1],
            content=f"User 1 message {i} in topic B",
            timestamp=now - timedelta(minutes=i + 10),
            metadata={"index": i, "topic": "topic_b"},
        )
        await topics["topic_b"].add_message(msg)

    # Add 6 messages from user_1 to topic_c
    for i in range(6):
        msg = Message(
            id=str(uuid.uuid4()),
            userId=user_ids[1],
            content=f"User 1 message {i} in topic C",
            timestamp=now - timedelta(minutes=i + 15),
            metadata={"index": i, "topic": "topic_c"},
        )
        await topics["topic_c"].add_message(msg)

    # User 2 has no messages initially

    return user_ids, topic_names


@pytest.mark.asyncio
async def test_get_user_messages_basic(setup_test_data):
    """Test basic functionality of getting a user's messages"""
    user_ids, _ = await setup_test_data

    # Test for user_0 who has messages in topics A and B
    response = client.get(f"/users/{user_ids[0]}/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user_ids[0]
    assert data["total"] == 8  # 5 in topic A + 3 in topic B
    assert len(data["messages"]) == 8

    # Verify messages contain correct user ID
    for msg in data["messages"]:
        assert msg["message"]["userId"] == user_ids[0]

    # Verify correct sorting (newest first)
    timestamps = [msg["message"]["timestamp"] for msg in data["messages"]]
    assert timestamps == sorted(timestamps, reverse=True)

    # Test for user_1 who has messages in topics B and C
    response = client.get(f"/users/{user_ids[1]}/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 10  # 4 in topic B + 6 in topic C

    # Test for user_2 who has no messages
    response = client.get(f"/users/{user_ids[2]}/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert len(data["messages"]) == 0


@pytest.mark.asyncio
async def test_user_messages_pagination(setup_test_data):
    """Test pagination of user messages endpoint"""
    user_ids, _ = await setup_test_data

    # Test pagination for user_1 who has 10 messages total
    # First page (default: 50 items)
    response = client.get(f"/users/{user_ids[1]}/messages")
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 10  # All messages

    # First page with custom limit
    response = client.get(f"/users/{user_ids[1]}/messages?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 5
    assert data["skip"] == 0
    assert data["limit"] == 5
    first_page_ids = [msg["message"]["id"] for msg in data["messages"]]

    # Second page
    response = client.get(f"/users/{user_ids[1]}/messages?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 5
    assert data["skip"] == 5
    assert data["limit"] == 5
    second_page_ids = [msg["message"]["id"] for msg in data["messages"]]

    # Make sure pages don't overlap
    assert not set(first_page_ids).intersection(set(second_page_ids))

    # Make sure ordering is preserved across pages
    response_all = client.get(f"/users/{user_ids[1]}/messages?limit=10")
    all_ids = [msg["message"]["id"] for msg in response_all.json()["messages"]]
    assert all_ids[:5] == first_page_ids
    assert all_ids[5:10] == second_page_ids

    # Test skip beyond available data
    response = client.get(f"/users/{user_ids[1]}/messages?skip=15")
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 0


@pytest.mark.asyncio
async def test_user_messages_nonexistent_user():
    """Test retrieving messages for a non-existent user"""
    fake_user_id = "nonexistent_user_" + str(uuid.uuid4())

    response = client.get(f"/users/{fake_user_id}/messages")
    assert response.status_code == 200  # Should return 200 even for non-existent users

    data = response.json()
    assert data["user_id"] == fake_user_id
    assert data["total"] == 0
    assert len(data["messages"]) == 0


@pytest.mark.asyncio
async def test_user_messages_topic_information(setup_test_data):
    """Test that messages include correct topic information"""
    user_ids, topic_names = await setup_test_data

    response = client.get(f"/users/{user_ids[0]}/messages")
    assert response.status_code == 200

    # Check that each message has associated topic information
    messages = response.json()["messages"]

    # Group messages by topic
    topic_message_counts = {}
    for msg in messages:
        topic_name = msg["topic"]["name"]
        if topic_name not in topic_message_counts:
            topic_message_counts[topic_name] = 0
        topic_message_counts[topic_name] += 1

    # User 0 should have 5 messages in topic_a and 3 in topic_b
    assert topic_message_counts["topic_a"] == 5
    assert topic_message_counts["topic_b"] == 3
    assert "topic_c" not in topic_message_counts


@pytest.mark.asyncio
async def test_user_messages_metadata_preserved(setup_test_data):
    """Test that message metadata is preserved in the response"""
    user_ids, _ = await setup_test_data

    response = client.get(f"/users/{user_ids[0]}/messages")
    assert response.status_code == 200

    # Check metadata in each message
    messages = response.json()["messages"]
    for msg in messages:
        metadata = msg["message"]["metadata"]
        assert "index" in metadata
        assert "topic" in metadata


@pytest.mark.asyncio
async def test_user_messages_query_validation(setup_test_data):
    """Test validation of query parameters"""
    user_ids, _ = await setup_test_data

    # Test negative skip
    response = client.get(f"/users/{user_ids[0]}/messages?skip=-5")
    assert response.status_code == 422  # Unprocessable Entity

    # Test excessively large limit
    response = client.get(f"/users/{user_ids[0]}/messages?limit=1000")
    assert response.status_code == 422  # Unprocessable Entity

    # Test zero limit
    response = client.get(f"/users/{user_ids[0]}/messages?limit=0")
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_add_and_retrieve_user_message(setup_test_data):
    """Test adding a new message and then retrieving it via the user endpoint"""
    user_ids, topic_names = await setup_test_data

    # Add a new message for user_2 (who previously had no messages)
    new_message = {
        "userId": user_ids[2],
        "content": "This is a new test message",
        "metadata": {"test": True},
    }

    response = client.post(f"/topics/{topic_names[0]}/messages", json=new_message)
    assert response.status_code == 200
    new_message_id = response.json()["id"]

    # Now retrieve user's messages
    response = client.get(f"/users/{user_ids[2]}/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["messages"][0]["message"]["id"] == new_message_id
    assert data["messages"][0]["message"]["content"] == new_message["content"]
    assert data["messages"][0]["topic"]["name"] == topic_names[0]
