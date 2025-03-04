import pytest
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException

# Add the parent directory to the path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the auth service module
from locavox.services.auth_service import (
    get_current_user,
    get_current_user_optional,
    authenticate_user,
    create_access_token,
    register_user,
    get_user_by_id,
)
from locavox.models.user import User, UserCreate
from locavox import config

# Import JWT libraries - these are used in tests even if not in the actual service
try:
    from jose import jwt
except ImportError:
    pytest.skip(
        "python-jose not installed, skipping auth tests", allow_module_level=True
    )

# Setup minimal test logger
import logging

logger = logging.getLogger("test_auth_service")


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return User(
        id="user-testuser",
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
    )


@pytest.fixture
def test_token(mock_user):
    """Create a test token for the mock user"""
    data = {
        "sub": mock_user.id,
        "username": mock_user.username,
        "email": mock_user.email,
        "is_admin": False,
    }
    token = create_access_token(data)
    return token


@pytest.fixture
def admin_token():
    """Create a test token with admin privileges"""
    data = {
        "sub": "user-admin",
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
    }
    token = create_access_token(data)
    return token


# Mark all tests in this class as async
pytestmark = pytest.mark.asyncio


class TestAuthService:
    """Test cases for auth_service module"""

    @pytest.mark.asyncio
    async def test_create_access_token(self):
        """Test that create_access_token generates a valid JWT token"""
        # Arrange
        test_data = {"sub": "test-user", "username": "testuser"}

        # Act
        token = create_access_token(test_data)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # Verify token content
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        assert payload["sub"] == test_data["sub"]
        assert payload["username"] == test_data["username"]
        assert "exp" in payload

    async def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiration"""
        # Arrange
        test_data = {"sub": "test-user"}
        expires_delta = timedelta(minutes=15)

        # Record current time before token creation - use timezone-aware datetime
        now_before = datetime.now(timezone.utc)

        # Act
        token = create_access_token(test_data, expires_delta)

        # Record time after token creation
        now_after = datetime.now(timezone.utc)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # Decode and verify token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        assert payload["sub"] == test_data["sub"]

        # Get the expiration timestamp from token
        exp_timestamp = payload["exp"]

        # Calculate expected expiration
        now = datetime.now(timezone.utc).timestamp()
        expected_exp = now + expires_delta.total_seconds()

        # Allow for a small time difference (up to 10 seconds) to account for test execution time
        assert abs(exp_timestamp - expected_exp) < 10, (
            f"Token expiration {exp_timestamp} should be close to {expected_exp}"
        )

        # Additional check - make sure exp is set properly in the future
        assert exp_timestamp > now, "Token should expire in the future"

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_valid_token(
        self, mock_get_user, test_token, mock_user
    ):
        """Test getting current user with a valid token"""
        # Arrange - properly mock the async function
        # Set the return value directly without wrapping in AsyncMock
        mock_get_user.return_value = mock_user

        # Act
        user = await get_current_user(test_token)

        # Assert
        assert user is not None
        assert user.id == mock_user.id
        assert user.username == mock_user.username

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_invalid_token(self, mock_get_user):
        """Test that invalid tokens are rejected"""
        # Arrange
        # Create an invalid token
        invalid_token = "invalid.token.format"

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(invalid_token)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_get_user.assert_not_called()

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_expired_token(self, mock_get_user):
        """Test that expired tokens are rejected"""
        # Arrange
        # Create an expired token
        data = {
            "sub": "test-user",
            "exp": (datetime.now(timezone.utc) - timedelta(days=1)).timestamp(),
        }
        expired_token = jwt.encode(data, config.SECRET_KEY, algorithm=config.ALGORITHM)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(expired_token)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_get_user.assert_not_called()

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_no_token(self, mock_get_user):
        """Test that missing token causes 401 error"""
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(None)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_get_user.assert_not_called()

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_missing_user(self, mock_get_user, test_token):
        """Test behavior when user ID in token doesn't exist"""
        # Arrange - fix how None is returned from the async function
        mock_get_user.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(test_token)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_get_user.assert_called_once()

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_optional_no_token(self, mock_get_user):
        """Test optional user returns None when no token provided"""
        # Act
        result = await get_current_user_optional(None)

        # Assert
        assert result is None
        mock_get_user.assert_not_called()

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_optional_with_token(
        self, mock_get_user, test_token, mock_user
    ):
        """Test optional user returns user when valid token provided"""
        # Arrange - fix the mock return value
        mock_get_user.return_value = mock_user

        # Act
        user = await get_current_user_optional(test_token)

        # Assert
        assert user is not None
        assert user.id == mock_user.id

    @patch("locavox.services.auth_service.get_user_by_id")
    async def test_get_current_user_optional_invalid_token(self, mock_get_user):
        """Test optional user returns None with invalid token"""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act
        result = await get_current_user_optional(invalid_token)

        # Assert
        assert result is None
        mock_get_user.assert_not_called()

    async def test_authenticate_user_success(self):
        """Test successful authentication"""
        # Arrange & Act
        username = "testuser"
        user = await authenticate_user(username, username)  # Using simple match rule

        # Assert
        assert user is not None
        assert user.username == username
        assert user.id == f"user-{username}"

    async def test_authenticate_user_failure(self):
        """Test failed authentication"""
        # Arrange & Act
        user = await authenticate_user("testuser", "wrongpassword")

        # Assert
        assert user is None

    async def test_authenticate_user_empty_credentials(self):
        """Test authentication with empty credentials"""
        # Arrange & Act
        user1 = await authenticate_user("", "password")
        user2 = await authenticate_user("username", "")

        # Assert
        assert user1 is None
        assert user2 is None

    async def test_register_user(self):
        """Test user registration"""
        # Arrange
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123",
            full_name="New User",
        )

        # Act
        new_user = await register_user(user_data)

        # Assert
        assert new_user is not None
        assert new_user.username == user_data.username
        assert new_user.email == user_data.email
        assert new_user.full_name == user_data.full_name
        assert new_user.id == f"user-{user_data.username}"
        assert new_user.is_active is True

    async def test_get_user_by_id_existing(self):
        """Test retrieving an existing user"""
        # Arrange
        test_id = "user-testuser"

        # Act
        user = await get_user_by_id(test_id)

        # Assert
        assert user is not None
        assert user.id == test_id
        assert user.username == "testuser"

    async def test_get_user_by_id_nonexistent(self):
        """Test retrieving a nonexistent user"""
        # Arrange & Act
        user = await get_user_by_id("nonexistent-id")

        # Assert
        assert user is None


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
