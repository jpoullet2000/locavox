import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

# Import the auth service module
from locavox.services.auth_service import (
    get_current_user,
    get_current_user_optional,
    authenticate_user,
    create_access_token,
)
from locavox.models.sql.user import User
from locavox.models.schemas.user import TokenData
from locavox import config

# Import JWT libraries
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
        first_name="Test",
        last_name="User",
        hashed_password="hashed_password_here",
        is_active=True,
    )


@pytest.fixture
def test_token(mock_user):
    """Create a test token for the mock user"""
    data = {
        "sub": mock_user.id,
    }
    token = create_access_token(data)
    return token


@pytest.fixture
def admin_token():
    """Create a test token with admin privileges"""
    data = {
        "sub": "user-admin",
    }
    token = create_access_token(data)
    return token


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = AsyncMock(spec=AsyncSession)
    return session


# Mark all tests in this class as async
pytestmark = pytest.mark.asyncio


class TestAuthService:
    """Test cases for auth_service module"""

    async def test_create_access_token(self):
        """Test that create_access_token generates a valid JWT token"""
        # Arrange
        test_data = {"sub": "test-user"}

        # Act
        token = create_access_token(test_data)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # Verify token content
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        assert payload["sub"] == test_data["sub"]
        assert "exp" in payload

    async def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiration"""
        # Arrange
        test_data = {"sub": "test-user"}
        expires_delta = timedelta(minutes=15)

        # Record current time before token creation - use timezone-aware datetime
        before_creation = datetime.now(timezone.utc)

        # Act
        token = create_access_token(test_data, expires_delta)

        # Record time after token creation
        after_creation = datetime.now(timezone.utc)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # Decode and verify token
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
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

    async def test_authenticate_user_success(self, mock_db_session, mock_user):
        """Test successful authentication"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        with patch("locavox.services.auth_service.verify_password", return_value=True):
            # Act
            user = await authenticate_user(mock_db_session, "testuser", "password123")

            # Assert
            assert user is not None
            assert user.username == mock_user.username
            assert user.id == mock_user.id
            mock_db_session.execute.assert_called_once()

    async def test_authenticate_user_wrong_password(self, mock_db_session, mock_user):
        """Test authentication with wrong password"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        with patch("locavox.services.auth_service.verify_password", return_value=False):
            # Act
            user = await authenticate_user(mock_db_session, "testuser", "wrongpassword")

            # Assert
            assert user is None
            mock_db_session.execute.assert_called_once()

    async def test_authenticate_user_nonexistent(self, mock_db_session):
        """Test authentication with nonexistent user"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        user = await authenticate_user(mock_db_session, "nonexistentuser", "password")

        # Assert
        assert user is None
        mock_db_session.execute.assert_called_once()

    async def test_get_current_user_valid_token(
        self, mock_db_session, test_token, mock_user
    ):
        """Test getting current user with a valid token"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        user = await get_current_user(test_token, mock_db_session)

        # Assert
        assert user is not None
        assert user.id == mock_user.id
        assert user.username == mock_user.username
        mock_db_session.execute.assert_called_once()

    async def test_get_current_user_invalid_token(self, mock_db_session):
        """Test that invalid tokens are rejected"""
        # Arrange
        # Create an invalid token
        invalid_token = "invalid.token.format"

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(invalid_token, mock_db_session)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_db_session.execute.assert_not_called()

    async def test_get_current_user_expired_token(self, mock_db_session):
        """Test that expired tokens are rejected"""
        # Arrange
        # Create an expired token
        data = {
            "sub": "test-user",
            "exp": (datetime.now(timezone.utc) - timedelta(days=1)).timestamp(),
        }
        expired_token = jwt.encode(
            data, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM
        )

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(expired_token, mock_db_session)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_db_session.execute.assert_not_called()

    async def test_get_current_user_missing_user(self, mock_db_session, test_token):
        """Test behavior when user ID in token doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(test_token, mock_db_session)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_db_session.execute.assert_called_once()

    async def test_get_current_user_optional_no_token(self, mock_db_session):
        """Test optional user returns None when no token provided"""
        # Act
        result = await get_current_user_optional(None, mock_db_session)

        # Assert
        assert result is None
        mock_db_session.execute.assert_not_called()

    async def test_get_current_user_optional_with_token(
        self, mock_db_session, test_token, mock_user
    ):
        """Test optional user returns user when valid token provided"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        user = await get_current_user_optional(test_token, mock_db_session)

        # Assert
        assert user is not None
        assert user.id == mock_user.id
        mock_db_session.execute.assert_called_once()

    async def test_get_current_user_optional_invalid_token(self, mock_db_session):
        """Test optional user returns None with invalid token"""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act
        result = await get_current_user_optional(invalid_token, mock_db_session)

        # Assert
        assert result is None
        mock_db_session.execute.assert_not_called()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
