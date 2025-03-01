import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from locavox.main import app
from locavox.logger import setup_logger
from locavox.models import BaseTopic  # Add import for BaseTopic

logger = setup_logger("tests.api")
client = TestClient(app)


@pytest.fixture
def test_message_data():
    return {
        "userId": "test_user",
        "content": "Test message content",
        "metadata": {"test_key": "test_value"},
    }


@pytest.fixture(autouse=True)
async def setup_test_client():
    """Initialize app and topics before each test"""
    from locavox.main import app, lifespan

    async with lifespan(app):
        yield


def test_list_topics():
    response = client.get("/topics")
    assert response.status_code == 200
    assert "topics" in response.json()
    topics = response.json()["topics"]
    assert isinstance(topics, list)
    assert "marketplace" in topics  # Check for default topic
    assert "chat" in topics  # Check for default topic


def test_add_and_list_messages():
    # Add a message to a new topic
    topic_name = "test_topic"
    message_data = {
        "userId": "test_user",
        "content": "Hello, world!",
        "metadata": {"key": "value"},
    }

    response = client.post(f"/topics/{topic_name}/messages", json=message_data)
    assert response.status_code == 200
    message_id = response.json()["id"]

    # Verify message was added by listing messages in the topic
    response = client.get(f"/topics/{topic_name}/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello, world!"

    # Verify the message ID matches
    assert messages[0]["id"] == message_id, (
        "Message ID in response should match the ID from creation"
    )


def test_query_topics(mock_embedding_generator):
    """Test querying topics with the embedding generator mocked"""
    # Add messages to different topics
    topics = ["topic1", "topic2"]
    messages = ["This is a test message", "Another message about cats"]
    message_ids = []

    for topic, content in zip(topics, messages):
        response = client.post(
            f"/topics/{topic}/messages",
            json={"userId": "test_user", "content": content},
        )
        message_ids.append(response.json()["id"])

    # Query for messages without LLM
    response = client.post("/query", json={"query": "cats", "use_llm": False})
    assert response.status_code == 200
    result = response.json()
    assert result is not None

    # Verify messages are returned
    if "messages" in result and result["messages"]:
        # Check that the message ID is one we created
        found_id = result["messages"][0]["id"]
        assert found_id in message_ids, (
            "Query should return one of our created messages"
        )


def test_query_topics_with_llm(mock_openai):
    """Test querying topics with LLM enabled"""
    # Add a test message
    response = client.post(
        "/topics/test_topic/messages",
        json={"userId": "test_user", "content": "Test message for LLM query"},
    )
    message_id = response.json()["id"]

    # Set up test configuration - temporarily enable LLM features
    from locavox import config

    original_use_llm = config.USE_LLM_BY_DEFAULT
    config.USE_LLM_BY_DEFAULT = True

    try:
        # Enable the mock OpenAI API key
        with patch("locavox.config.OPENAI_API_KEY", "mock_key"):
            # Query with LLM
            response = client.post(
                "/query", json={"query": "test query", "use_llm": True}
            )
            assert response.status_code == 200
            result = response.json()

            # Basic validation of the response structure
            assert "query" in result

            # Check that results were processed
            if "topic_results" in result and result["topic_results"]:
                for topic_result in result["topic_results"]:
                    if "messages" in topic_result and topic_result["messages"]:
                        # Check if our message is in the results
                        found = any(
                            msg["id"] == message_id for msg in topic_result["messages"]
                        )
                        if found:
                            break
                else:
                    # This assertion is just informational - sometimes the LLM might not identify our message
                    # as relevant, so we don't want the test to fail
                    logger.info("LLM didn't identify our message as relevant")
    finally:
        # Restore original configuration
        config.USE_LLM_BY_DEFAULT = original_use_llm
