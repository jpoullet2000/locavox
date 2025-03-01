import pytest
import os
from datetime import datetime
from locavox.base_models import Message  # Updated import
from locavox.models import BaseTopic


@pytest.fixture
def test_topic():
    """Create a test topic with sync initialization"""
    topic = BaseTopic("test_topic", "Test Topic Description")
    topic.initialize_sync()  # Initialize synchronously
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
        metadata={
            "test_key": "test_value"
        },  # This will be automatically converted to string
    )


@pytest.mark.asyncio
async def test_message_posting(test_topic, test_message):
    await test_topic.add_message(test_message)

    assert len(test_topic.messages) == 1
    assert test_topic.messages[0].content == test_message.content

    stored_messages = await test_topic.search_messages(test_message.content)
    assert len(stored_messages) == 1
    assert stored_messages[0].content == test_message.content
    assert stored_messages[0].userId == test_message.userId


@pytest.mark.asyncio
async def test_message_search(test_topic, test_message):
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
    assert len(results) == 1  # Fixed parentheses placement
    assert results[0].content == "Another test message"


@pytest.mark.asyncio
async def test_message_metadata_handling(test_topic, test_message):
    await test_topic.add_message(test_message)

    # Verify metadata is preserved
    stored_messages = await test_topic.search_messages(test_message.content)
    assert len(stored_messages) == 1
    retrieved_message = stored_messages[0]
    assert isinstance(retrieved_message.metadata, dict)
    assert retrieved_message.metadata["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_complex_metadata_handling(test_topic):
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
