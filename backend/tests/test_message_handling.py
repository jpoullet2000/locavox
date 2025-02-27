import pytest
import asyncio
from datetime import datetime
from locavox.base_models import Message  # Updated import
from locavox.models import BaseTopic
from locavox.storage import TopicStorage
import lancedb
import os


@pytest.fixture
def test_topic():
    topic = BaseTopic("test_topic", "Test Topic Description")
    topic.storage.initialize()  # Initialize synchronously
    return topic


@pytest.fixture(autouse=True)
async def cleanup_test_topic():
    # Clean up before and after each test
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
    assert len(results == 1)
    assert results[0].content == "Another test message"
