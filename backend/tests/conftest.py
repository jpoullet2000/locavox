import pytest
import os
import shutil
import logging

# import sys
from unittest.mock import patch, MagicMock
from locavox import config
from locavox.logger import setup_logger
import tempfile
from fastapi.testclient import TestClient
from locavox.main import app

# Add the parent directory to the path so we can import from locavox
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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


@pytest.fixture
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

    # Create a dictionary of patches instead of a list
    patches = {}

    # Basic OpenAI patches that should work regardless
    patches["openai.OpenAI"] = mock_client
    patches["openai.AsyncOpenAI"] = mock_client

    # Conditionally add patches for modules that might not exist
    try:
        import locavox.llm_search

        patches["locavox.llm_search.client"] = mock_client
        patches["locavox.llm_search.async_client"] = mock_client
        test_logger.debug("Added LLM search patches")
    except ImportError:
        # Module doesn't exist, don't attempt to patch it
        test_logger.debug("locavox.llm_search module not found, skipping patch")

    # Apply all patches at once using patch.multiple
    with patch.multiple(
        "", **{target: patch(target, new=value) for target, value in patches.items()}
    ):
        yield mock_client


# Alternative implementation using individual patches if multiple doesn't work
@pytest.fixture
def mock_openai_alt():
    """Alternative implementation of mock_openai using individual context managers"""
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

    # Apply patches individually using nested context managers
    with patch("openai.OpenAI", return_value=mock_client):
        with patch("openai.AsyncOpenAI", return_value=mock_client):
            # Conditionally patch LLM search if it exists
            try:
                import locavox.llm_search

                with patch("locavox.llm_search.client", mock_client):
                    with patch("locavox.llm_search.async_client", mock_client):
                        yield mock_client
            except ImportError:
                # Module doesn't exist, continue without patching it
                test_logger.debug("locavox.llm_search module not found, skipping patch")
                yield mock_client


@pytest.fixture
def mock_embedding_generator():
    """Mock the embedding generator to return consistent test embeddings"""
    # Only mock if the module exists
    try:
        from locavox.embeddings import EmbeddingGenerator

        with patch("locavox.embeddings.EmbeddingGenerator.generate") as mock_generate:
            # Return a small consistent embedding for tests
            mock_generate.return_value = [0.1] * 384  # Small embedding for tests
            yield mock_generate
    except ImportError:
        # Module doesn't exist, return a simple mock
        yield MagicMock(return_value=[0.1] * 384)


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


# Add any global fixtures here that might be used across multiple test files
@pytest.fixture
def test_app():
    """Create a test application for FastAPI testing"""
    from fastapi.testclient import TestClient
    from locavox.main import app

    client = TestClient(app)
    return client
