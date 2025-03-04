import pytest
from datetime import datetime

# Import BaseTopic instead of Topic
from locavox.models import BaseTopic, Message


@pytest.fixture
async def test_topics():
    # Use BaseTopic instead of Topic
    topics = {
        "general": BaseTopic(name="general"),
        "support": BaseTopic(name="support"),
    }
    yield topics
    # Cleanup code here if needed


@pytest.mark.asyncio
async def test_cross_topic_search():
    # Create topics using BaseTopic instead of Topic
    topic1 = BaseTopic(name="topic1")
    topic2 = BaseTopic(name="topic2")

    # Add messages to both topics
    messages = [
        Message(
            id="1",
            content="Python programming discussion",
            userId="user1",
            timestamp=datetime.now(),
            metadata={"category": "programming"},
        ),
        Message(
            id="2",
            content="Python tutorial help needed",
            userId="user2",
            timestamp=datetime.now(),
            metadata={"category": "help"},
        ),
    ]

    await topic1.add_message(messages[0])
    await topic2.add_message(messages[1])

    # Search in both topics
    results1 = await topic1.search_messages("Python")
    results2 = await topic2.search_messages("Python")

    assert len(results1) == 1
    assert len(results2) == 1
    assert "programming" in results1[0].content
    assert "tutorial" in results2[0].content


@pytest.mark.asyncio
async def test_metadata_search():
    # Use BaseTopic with named parameter
    topic = BaseTopic(name="test")

    message = Message(
        id="1",
        content="Message with special metadata",
        userId="user1",
        timestamp=datetime.now(),
        metadata={
            "location": "New York",
            "tags": ["important", "urgent"],
            "priority": 1,
        },
    )

    await topic.add_message(message)
    results = await topic.search_messages("special metadata")

    assert len(results) == 1
    assert results[0].metadata["location"] == "New York"
    assert "important" in results[0].metadata["tags"]
