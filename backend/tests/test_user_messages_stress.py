import pytest
import uuid
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from locavox.main import app
from locavox.models import Message, Topic
from locavox.logger import setup_logger

# Set up logger for tests
logger = setup_logger("tests.user_messages_stress")

# Create a test client
client = TestClient(app)


@pytest.fixture
async def setup_stress_test_data(event_loop):
    """Setup larger dataset for stress testing"""
    from locavox.main import topics

    # Create test users
    num_users = 5
    user_ids = [f"stress_test_user_{i}" for i in range(num_users)]

    # Create test topics
    num_topics = 3
    topic_names = [f"stress_topic_{i}" for i in range(num_topics)]

    # Clear existing topics
    topics.clear()

    # Create fresh topics
    for name in topic_names:
        topics[name] = Topic(name)

    # Set up how many messages per user per topic
    messages_per_user_per_topic = 10

    # Add messages with timestamps in descending order
    now = datetime.now()
    total_msgs = 0

    start_time = time.time()

    # Add messages for each user in each topic
    for user_idx, user_id in enumerate(user_ids):
        for topic_idx, topic_name in enumerate(topic_names):
            for msg_idx in range(messages_per_user_per_topic):
                msg = Message(
                    id=str(uuid.uuid4()),
                    userId=user_id,
                    content=f"User {user_idx} message {msg_idx} in topic {topic_idx}",
                    timestamp=now
                    - timedelta(minutes=msg_idx + (user_idx * 100) + (topic_idx * 10)),
                    metadata={
                        "user_idx": user_idx,
                        "topic_idx": topic_idx,
                        "msg_idx": msg_idx,
                    },
                )
                await topics[topic_name].add_message(msg)
                total_msgs += 1

    setup_time = time.time() - start_time
    logger.info(f"Created {total_msgs} messages in {setup_time:.2f} seconds")

    return user_ids, topic_names


@pytest.mark.asyncio
async def test_user_messages_performance(setup_stress_test_data):
    """Test performance of retrieving user messages with larger dataset"""
    user_ids, _ = await setup_stress_test_data

    # Get the first user's messages and measure time
    user_id = user_ids[0]

    start_time = time.time()
    response = client.get(f"/users/{user_id}/messages")
    query_time = time.time() - start_time

    assert response.status_code == 200
    data = response.json()

    # Each user should have messages_per_user_per_topic * num_topics messages
    expected_count = 10 * 3  # messages_per_user_per_topic * num_topics
    assert data["total"] == expected_count

    # Log performance information
    logger.info(
        f"Retrieved {len(data['messages'])} messages in {query_time:.4f} seconds"
    )

    # Basic performance threshold check
    # This is a loose check that should pass on most systems
    assert query_time < 2.0, "Query took too long"


@pytest.mark.asyncio
async def test_user_messages_pagination_stress(setup_stress_test_data):
    """Test pagination with larger dataset"""
    user_ids, _ = await setup_stress_test_data
    user_id = user_ids[0]

    # Get all pages of results with small page size
    page_size = 5
    all_message_ids = []

    # Get first page
    response = client.get(f"/users/{user_id}/messages?limit={page_size}")
    assert response.status_code == 200
    data = response.json()
    total = data["total"]

    # Add first page of message IDs
    all_message_ids.extend([msg["message"]["id"] for msg in data["messages"]])

    # Get remaining pages
    for skip in range(page_size, total, page_size):
        response = client.get(
            f"/users/{user_id}/messages?skip={skip}&limit={page_size}"
        )
        assert response.status_code == 200
        data = response.json()
        all_message_ids.extend([msg["message"]["id"] for msg in data["messages"]])

    # Check for duplicate message IDs across pages
    assert len(all_message_ids) == len(set(all_message_ids)), (
        "Duplicate messages found across pages"
    )

    # Check that we got all messages
    assert len(all_message_ids) == total


@pytest.mark.asyncio
async def test_simultaneous_user_queries(setup_stress_test_data):
    """Test querying multiple users simultaneously"""
    import asyncio

    user_ids, _ = await setup_stress_test_data

    # Helper function to make async requests
    async def get_user_messages(user_id):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: client.get(f"/users/{user_id}/messages")
        )

    # Make concurrent requests for all users
    start_time = time.time()
    responses = await asyncio.gather(*[get_user_messages(uid) for uid in user_ids])
    total_time = time.time() - start_time

    # Log performance information
    logger.info(
        f"Retrieved messages for {len(user_ids)} users in {total_time:.4f} seconds"
    )

    # Check all responses are valid
    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert (
            data["total"] == 30
        )  # Each user should have 30 messages (10 per topic * 3 topics)
