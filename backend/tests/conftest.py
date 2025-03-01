import pytest
import os
import shutil
import logging
from unittest.mock import patch, MagicMock
from locavox import config
from locavox.logger import setup_logger
import tempfile
from fastapi.testclient import TestClient
from locavox.main import app

# Configure test logger
test_logger = setup_logger("tests", logging.DEBUG)


def pytest_configure(config):
    pytest.test_db_uri = "memory://test_db"

    # Reduce noise in test output by setting higher log levels for some loggers
    setup_logger("urllib3", logging.WARNING)
    setup_logger("asyncio", logging.WARNING)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Use absolute path for temporary test database
    # This avoids relative path issues that can occur in different test environments
    test_db_path = tempfile.mkdtemp(prefix="locavox_test_")
    original_db_path = config.DATABASE_PATH
    original_max_msgs = config.MAX_MESSAGES_PER_USER

    # Set up clean environment for tests
    config.DATABASE_PATH = test_db_path
    config.USE_LLM_BY_DEFAULT = False  # Disable LLM for tests

    test_logger.info(f"Using test database path: {test_db_path}")
    test_logger.info(f"Default message limit: {config.MAX_MESSAGES_PER_USER}")

    # Cleanup before test (should be fresh directory from tempfile)
    if not os.path.exists(test_db_path):
        os.makedirs(test_db_path)

    yield

    # Cleanup after test
    try:
        shutil.rmtree(test_db_path)
    except Exception as e:
        test_logger.warning(f"Failed to remove test data directory: {e}")

    # Restore original settings
    config.DATABASE_PATH = original_db_path
    config.MAX_MESSAGES_PER_USER = original_max_msgs


@pytest.fixture(autouse=True)
def mock_openai():
    """Mock OpenAI API calls to avoid requiring an API key during tests"""
    # Create mock completion response
    mock_completion_response = MagicMock()
    mock_completion_response.choices = [MagicMock()]
    mock_completion_response.choices[0].message.content = "Mocked OpenAI response"

    # Create mock embedding response
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock()]
    mock_embedding_response.data[0].embedding = [
        0.1
    ] * 1536  # Standard OpenAI embedding size

    # Create mock client
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        return_value=mock_completion_response
    )
    mock_client.embeddings.create = MagicMock(return_value=mock_embedding_response)

    # Patch both sync and async OpenAI clients
    with (
        patch("openai.OpenAI", return_value=mock_client),
        patch("openai.AsyncOpenAI", return_value=mock_client),
        patch("locavox.llm_search.client", mock_client),
        patch("locavox.llm_search.async_client", mock_client),
    ):
        yield mock_client


@pytest.fixture
def mock_embedding_generator():
    """Mock the embedding generator to return consistent test embeddings"""
    with patch("locavox.embeddings.EmbeddingGenerator.generate") as mock_generate:
        # Return a small consistent embedding for tests
        mock_generate.return_value = [0.1] * 384  # Small embedding for tests
        yield mock_generate


@pytest.fixture
def client():
    """Create a FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def reset_config():
    """Reset config values after test"""
    # Store original values
    original_msg_limit = config.MAX_MESSAGES_PER_USER

    # Return a function to restore values
    def _reset():
        config.MAX_MESSAGES_PER_USER = original_msg_limit

    yield
    # Restore values after test
    _reset()
