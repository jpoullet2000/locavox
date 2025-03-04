import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)


def test_get_topics():
    """Test that the /topics endpoint returns a list of topic objects with full attributes."""
    response = client.get("/topics")
    assert response.status_code == 200

    # Parse response data
    topics = response.json()

    # Check that we got a list
    assert isinstance(topics, list)

    # Check that each topic has the required attributes
    for topic in topics:
        assert "id" in topic
        assert "title" in topic
        assert "description" in topic
        assert isinstance(topic["id"], str)
        assert isinstance(topic["title"], str)
        assert isinstance(topic["description"], str)


def test_get_topic_by_id():
    """Test getting a specific topic by ID."""
    # First get all topics
    all_topics = client.get("/topics").json()

    # Then get the first topic by ID
    first_topic = all_topics[0]
    topic_id = first_topic["id"]

    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == 200

    # Check that the returned topic matches
    topic = response.json()
    assert topic["id"] == topic_id
    assert topic["title"] == first_topic["title"]
    assert topic["description"] == first_topic["description"]


def test_get_nonexistent_topic():
    """Test getting a topic that doesn't exist."""
    response = client.get("/topics/nonexistent-id")
    assert response.status_code == 404
