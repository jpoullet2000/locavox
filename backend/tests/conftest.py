import pytest
import os
import shutil
import logging
import asyncio
import uuid
from unittest.mock import patch, MagicMock
from locavox import config
from locavox.logger import setup_logger
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
import sys
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from locavox.main import app
from locavox.database import get_db_session
from locavox.models.sql.base import Base
from locavox.models.sql.user import User
from locavox.services.auth_service import create_access_token
from locavox.utils.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
# Configure test logger
test_logger = setup_logger("tests", logging.DEBUG)


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create a shared test engine for all tests"""
    # Create the engine with a shared cache parameter
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:?cache=shared",
        echo=True,
        poolclass=StaticPool,  # Important for shared memory connection
    )

    # Create initial tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up tables after tests are done
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# # Create test engine
# test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

# # Create test session factory
# TestSessionLocal = sessionmaker(
#     test_engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False,
# )


# # Override the get_db_session dependency
# async def override_get_db_session():
#     async with TestSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()


# # Test client with overridden dependencies
# @pytest.fixture
# def client():
#     app.dependency_overrides[get_db_session] = override_get_db_session
#     with TestClient(app) as test_client:
#         yield test_client
#     app.dependency_overrides = {}


# @pytest.fixture
# async def override_get_db_session(test_db_engine):
#     """Get database session from the shared engine"""
#     # Create session factory from the shared engine
#     TestSessionLocal = sessionmaker(
#         test_db_engine,
#         class_=AsyncSession,
#         expire_on_commit=False,
#         autoflush=False,
#     )

#     # Yield the session
#     async with TestSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()


@pytest.fixture
async def override_get_db_session(test_db_engine):
    """Get database session from the shared engine"""
    # Create session factory from the shared engine
    TestSessionLocal = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def _override_get_db_session():
        async with TestSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    return _override_get_db_session  # Return the function, not the session


@pytest.fixture
def client(override_get_db_session):
    """Test client with the shared database session"""
    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}


@pytest.fixture(scope="session", autouse=True)
async def setup_test_environment(test_db_engine):
    """Setup test environment

    This fixture is run before each test to set up the test environment.
    """
    # Use absolute path for temporary test database
    # This avoids relative path issues that can occur in different test environments
    test_db_path = tempfile.mkdtemp(prefix="locavox_test_")
    original_db_path = config.DATABASE_PATH
    original_max_msgs = config.MAX_MESSAGES_PER_USER

    # Set up clean environment for tests
    config.DATABASE_PATH = test_db_path
    config.USE_LLM_BY_DEFAULT = False  # Disable LLM for tests
    config.settings.TESTING = True  # Make sure TESTING flag is set
    config.settings.DATABASE_RECREATE_TABLES = True  # Force table recreation

    test_logger.info(f"Using test database path: {test_db_path}")
    test_logger.info(f"Default message limit: {config.MAX_MESSAGES_PER_USER}")

    # Cleanup before test (should be fresh directory from tempfile)
    if not os.path.exists(test_db_path):
        os.makedirs(test_db_path)

    # Import here to avoid circular imports
    # from locavox.database import init_db

    # Initialize database tables
    # await init_db()
    from sqlalchemy import text

    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        # async with TestSessionLocal() as session:
        # Override the get_db_session dependency
        # app.dependency_overrides[get_db_session] = override_get_db_session

        # Yield the session for the test
        tables = await conn.run_sync(
            lambda sync_conn: sync_conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            ).fetchall()
        )
        # tables_created = [row[0] for row in result]
        # result = await session.execute(
        #     text("SELECT name FROM sqlite_master WHERE type='table';")
        # )
        # tables = [row[0] for row in result.fetchall()]
        test_logger.info(f"Tables created in test DB: {tables}")
        # session = await override_get_db_session()
        yield

    # Cleanup after test
    try:
        shutil.rmtree(test_db_path)
    except Exception as e:
        test_logger.warning(f"Failed to remove test data directory: {e}")

    # Restore original settings
    config.DATABASE_PATH = original_db_path
    config.MAX_MESSAGES_PER_USER = original_max_msgs


# # Create test database and tables
# @pytest.fixture(scope="session")
# async def init_test_db():
#     # Create tables
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

#     yield

#     # Drop tables
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# Create a test user and return authentication token
# @pytest.fixture
# # async def test_user(init_test_db):
# async def test_user():
#     user_id = "test_user_id"

#     async with TestSessionLocal() as session:
#         # Check if user already exists
#         from sqlalchemy import select

#         result = await session.execute(select(User).where(User.id == user_id))
#         existing_user = result.scalar_one_or_none()

#         if existing_user is None:
#             # Create test user
#             user = User(
#                 id=user_id,
#                 email="test@example.com",
#                 username="testuser",
#                 hashed_password=get_password_hash("password123"),
#                 is_active=True,
#             )
#             session.add(user)
#             await session.commit()
#             await session.refresh(user)
#         else:
#             user = existing_user

#         # Create token
#         access_token = create_access_token(
#             data={"sub": user.id}, expires_delta=timedelta(minutes=30)
#         )

#         # Override the auth dependency
#         app.dependency_overrides[get_db_session] = override_get_db_session

#         yield {
#             "user": user,
#             "token": access_token,
#             "auth_header": {"Authorization": f"Bearer {access_token}"},
#         }


@pytest.fixture
async def test_user(test_db_engine):
    """Create a test user with authentication token"""
    user_id = str(uuid.uuid4())

    # Create session factory from the shared engine
    TestSessionLocal = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with TestSessionLocal() as session:
        # Check if user already exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.id == user_id))
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            # Create test user
            user = User(
                id=user_id,
                email="test@example.com",
                username="testuser",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            user = existing_user

        # Create token
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=timedelta(minutes=30)
        )

        yield {
            "user": user,
            "token": access_token,
            "auth_header": {"Authorization": f"Bearer {access_token}"},
        }


@pytest.fixture
async def test_superuser(test_db_engine):
    """Create a test superuser with authentication token"""
    superuser_id = str(uuid.uuid4())

    # Create session factory from the shared engine
    TestSessionLocal = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with TestSessionLocal() as session:
        # Check if superuser already exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.id == superuser_id))
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            # Create test superuser
            user = User(
                id=superuser_id,
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,  # This is the key difference
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            user = existing_user

        # Create token
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=timedelta(minutes=30)
        )

        yield {
            "user": user,
            "token": access_token,
            "auth_header": {"Authorization": f"Bearer {access_token}"},
        }


@pytest.fixture
async def test_topic(test_db_engine):
    """Create a test topic and return it"""
    from locavox.models.sql.topic import Topic  # Import the Topic model

    # Generate a unique ID for the topic
    import uuid

    topic_id = str(uuid.uuid4())

    # Create session factory from the shared engine
    TestSessionLocal = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with TestSessionLocal() as session:
        # Create test topic
        topic = Topic(
            id=topic_id,
            title="Test Topic",
            description="This is a test topic created for testing purposes",
            # Add any other required fields here
            category="test category",
        )

        session.add(topic)
        await session.commit()
        await session.refresh(topic)

        yield {"topic": topic, "id": topic_id}


# @pytest.fixture
# async def test_topic():
#     """Create a test topic and return it"""
#     from locavox.models.sql.topic import Topic  # Import the Topic model

#     # Generate a unique ID for the topic
#     import uuid

#     topic_id = str(uuid.uuid4())

#     async with TestSessionLocal() as session:
#         # Create test topic
#         topic = Topic(
#             id=topic_id,
#             title="Test Topic",
#             description="This is a test topic created for testing purposes",
#             # Add any other required fields here
#             category="test category",
#         )

#         session.add(topic)
#         await session.commit()
#         await session.refresh(topic)

#         yield {"topic": topic, "id": topic_id}


# Setup and teardown the test database
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure():
    pytest.test_db_uri = "memory://test_db"

    # Reduce noise in test output by setting higher log levels for some loggers
    setup_logger("urllib3", logging.WARNING)
    setup_logger("asyncio", logging.WARNING)

    # Enable testing mode
    config.settings.TESTING = True

    # Enable database table recreation for tests
    config.settings.DATABASE_RECREATE_TABLES = True


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
        import locavox.llm_search  # noqa: F401

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
                import locavox.llm_search  # noqa: F401

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
        from locavox.embeddings import EmbeddingGenerator  # noqa: F401

        with patch("locavox.embeddings.EmbeddingGenerator.generate") as mock_generate:
            # Return a small consistent embedding for tests
            mock_generate.return_value = [0.1] * 384  # Small embedding for tests
            yield mock_generate
    except ImportError:
        # Module doesn't exist, return a simple mock
        yield MagicMock(return_value=[0.1] * 384)


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
