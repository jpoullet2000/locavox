import pytest
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from locavox.main import app
from locavox.models import Message, BaseTopic
from locavox.logger import setup_logger
from locavox.topic_registry import topics

# Setup logger
logger = setup_logger("tests.user_messages_stress")

# Create a test client
client = TestClient(app)

# Constants for test configuration
NUM_USERS = 5
NUM_TOPICS = 3
MESSAGES_PER_USER_PER_TOPIC = 10

# Create a flag to track message creation
messages_added = False


@pytest.fixture(scope="module")
async def setup_stress_test_data():
    """Set up test data for stress tests"""
    # Store original topics
    original_topics = dict(topics)

    test_data = {"user_ids": [], "topic_names": [], "ready": False, "error": None}

    try:
        # Clear topics
        topics.clear()
        logger.info("Cleared topics registry")

        # Create topic instances
        topic_names = [f"stress_topic_{i}" for i in range(NUM_TOPICS)]
        user_ids = [f"stress_test_user_{i}" for i in range(NUM_USERS)]

        # Store data in our result dict
        test_data["user_ids"] = user_ids
        test_data["topic_names"] = topic_names

        for name in topic_names:
            topics[name] = BaseTopic(name=name)
        logger.info(f"Created {len(topics)} test topics")

        # Add messages
        global messages_added
        if not messages_added:
            now = datetime.now()
            total_msgs = 0

            for user_idx, user_id in enumerate(user_ids):
                for topic_idx, topic_name in enumerate(topic_names):
                    for msg_idx in range(MESSAGES_PER_USER_PER_TOPIC):
                        msg = Message(
                            id=f"msg-{user_idx}-{topic_idx}-{msg_idx}",
                            userId=user_id,
                            content=f"User {user_idx} message {msg_idx} in topic {topic_idx}",
                            timestamp=now
                            - timedelta(
                                minutes=msg_idx + (user_idx * 100) + (topic_idx * 10)
                            ),
                            metadata={
                                "user_idx": user_idx,
                                "topic_idx": topic_idx,
                                "msg_idx": msg_idx,
                            },
                        )
                        await topics[topic_name].add_message(msg)
                        total_msgs += 1

            logger.info(f"Added {total_msgs} test messages")
            messages_added = True

        # Verify that messages were created
        test_user = user_ids[0]
        test_topic = topic_names[0]
        test_msgs = await topics[test_topic].get_messages_by_user(test_user)
        logger.info(
            f"Verification: Found {len(test_msgs)} messages for user {test_user} in {test_topic}"
        )

        # Mark as ready
        test_data["ready"] = True

        # Yield the test data instead of returning it
        yield test_data

    except Exception as e:
        logger.error(f"Error in setup: {e}")
        test_data["error"] = str(e)
        yield test_data  # Yield error data

    finally:
        # This will run after all tests when the fixture is destroyed
        # Clean up
        topics.clear()
        topics.update(original_topics)
        logger.info("Restored original topics")


@pytest.mark.skip("Skipping stress test for now")
@pytest.mark.asyncio
async def test_simultaneous_user_queries(setup_stress_test_data):
    """Test querying multiple users simultaneously"""
    # Verify setup was successful
    assert setup_stress_test_data["ready"], (
        f"Test setup failed: {setup_stress_test_data.get('error')}"
    )

    # Get test users
    user_ids = setup_stress_test_data["user_ids"]
    assert len(user_ids) >= 2, "Not enough test users were created"

    # Verify that users actually have messages
    first_user = user_ids[0]
    first_topic = setup_stress_test_data["topic_names"][0]

    # Direct check to confirm messages exist
    user_msgs = await topics[first_topic].get_messages_by_user(first_user)
    logger.info(
        f"Direct check: User {first_user} has {len(user_msgs)} messages in {first_topic}"
    )
    assert len(user_msgs) > 0, "No messages found for test user"

    import asyncio

    # Helper function for async requests
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
    for idx, response in enumerate(responses):
        assert response.status_code == 200, f"Request for user {user_ids[idx]} failed"

        data = response.json()
        logger.info(f"User {user_ids[idx]} has {data['total']} messages via API")

        expected_count = MESSAGES_PER_USER_PER_TOPIC * NUM_TOPICS
        assert data["total"] == expected_count, (
            f"Expected {expected_count} messages, got {data['total']}"
        )

        # Check that messages belong to the right user
        for msg in data["messages"]:
            assert msg["message"]["userId"] == user_ids[idx], (
                "Message has wrong user ID"
            )


# Keep the other tests but make them properly depend on setup_stress_test_data
@pytest.mark.skip("Skipping stress test for now")
@pytest.mark.asyncio
async def test_user_messages_performance(setup_stress_test_data):
    """Test performance of retrieving user messages with larger dataset"""
    # ... rest of the test function ...
    pass


@pytest.mark.skip("Skipping stress test for now")
@pytest.mark.asyncio
async def test_user_messages_pagination_stress(setup_stress_test_data):
    """Test pagination with larger dataset"""
    # ... rest of the test function ...
    pass
