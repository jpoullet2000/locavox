import pytest
import os
from datetime import datetime
from locavox.models import Message, BaseTopic


@pytest.fixture
def test_topic():
    """Create a test topic"""
    # Create the topic without any initialization - your BaseTopic doesn't have initialize_sync
    topic = BaseTopic(name="test_topic", description="Test Topic Description")
    return topic


@pytest.fixture(autouse=True)
async def cleanup_test_topic():
    """Clean up the test database before and after each test"""
    db_path = "data/test_topic"
    if os.path.exists(db_path):
        import shutil

        shutil.rmtree(db_path)
    yield
    if os.path.exists(db_path):
        shutil.rmtree(db_path)


@pytest.fixture
def test_message():
    return Message(
        id="test_id_123",
        content="Test message content",
        userId="test_user",
        timestamp=datetime.now(),
        metadata={"test_key": "test_value"},
    )


@pytest.mark.asyncio
async def test_message_posting(test_topic, test_message):
    """Test adding a message to a topic"""
    await test_topic.add_message(test_message)

    # Get recent messages and check them
    messages = await test_topic.get_messages(limit=10)
    assert len(messages) == 1
    assert messages[0].content == test_message.content

    # Use the search method to find the message
    stored_messages = await test_topic.search_messages(test_message.content)
    assert len(stored_messages) == 1
    assert stored_messages[0].content == test_message.content
    assert stored_messages[0].userId == test_message.userId


@pytest.mark.asyncio
async def test_message_search(test_topic, test_message):
    """Test searching for messages in a topic"""
    await test_topic.add_message(test_message)

    second_message = Message(
        id="test_id_456",
        content="Another test message",
        userId="test_user",
        timestamp=datetime.now(),
        metadata={},
    )
    await test_topic.add_message(second_message)

    # Test search functionality
    results = await test_topic.search_messages("test message")
    assert len(results) == 2

    results = await test_topic.search_messages("Another")
    assert len(results) == 1
    assert results[0].content == "Another test message"


@pytest.mark.asyncio
async def test_message_metadata_handling(test_topic, test_message):
    """Test that message metadata is preserved"""
    await test_topic.add_message(test_message)

    # Verify metadata is preserved
    stored_messages = await test_topic.search_messages(test_message.content)
    assert len(stored_messages) == 1
    retrieved_message = stored_messages[0]
    assert isinstance(retrieved_message.metadata, dict)
    assert retrieved_message.metadata["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_complex_metadata_handling(test_topic):
    """Test handling of complex metadata structures"""
    complex_message = Message(
        id="test_id_789",
        content="Message with complex metadata",
        userId="test_user",
        timestamp=datetime.now(),
        metadata={
            "numbers": [1, 2, 3],
            "nested": {"key": "value"},
            "mixed": [{"a": 1}, {"b": 2}],
        },
    )

    await test_topic.add_message(complex_message)
    results = await test_topic.search_messages("complex metadata")

    assert len(results) == 1
    retrieved = results[0]
    assert retrieved.metadata["numbers"] == [1, 2, 3]
    assert retrieved.metadata["nested"]["key"] == "value"
    assert retrieved.metadata["mixed"][0]["a"] == 1


@pytest.mark.asyncio
async def test_get_messages_by_user(test_topic):
    """Test retrieving messages from a specific user"""
    # Add messages from different users
    user1_msg1 = Message(
        id="user1_msg1",
        content="Message from user 1",
        userId="user1",
        timestamp=datetime.now(),
        metadata={},
    )
    user1_msg2 = Message(
        id="user1_msg2",
        content="Another message from user 1",
        userId="user1",
        timestamp=datetime.now(),
        metadata={},
    )
    user2_msg = Message(
        id="user2_msg",
        content="Message from user 2",
        userId="user2",
        timestamp=datetime.now(),
        metadata={},
    )

    await test_topic.add_message(user1_msg1)
    await test_topic.add_message(user1_msg2)
    await test_topic.add_message(user2_msg)

    # Retrieve messages for user1
    user1_messages = await test_topic.get_messages_by_user("user1")
    assert len(user1_messages) == 2
    assert all(msg.userId == "user1" for msg in user1_messages)

    # Retrieve messages for user2
    user2_messages = await test_topic.get_messages_by_user("user2")
    assert len(user2_messages) == 1
    assert user2_messages[0].userId == "user2"
