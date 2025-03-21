from locavox.services import auth_service
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, status, HTTPException  # Added HTTPException import
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime  # Added datetime import

from locavox.routers.auth import router
from locavox.models.sql.user import User
from locavox.models.schemas.user import UserCreate, UserResponse
from locavox.services.user_service import UserExistsError

# Create a test app with proper dependency overrides
app = FastAPI()
app.include_router(router)


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    db = AsyncMock(spec=AsyncSession)
    return db


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
        is_superuser=False,  # Added missing field
        created_at=datetime.utcnow(),  # Added missing field
    )


@pytest.fixture
def created_user():
    """Create a mock user that matches registration data"""
    return User(
        id="user-newuser",
        username="newuser",
        email="new@example.com",
        first_name="New",
        last_name="User",
        hashed_password="hashed_password_here",
        is_active=True,
        is_superuser=False,  # Added missing field
        created_at=datetime.utcnow(),  # Added missing field
    )


@pytest.fixture
def test_client(mock_db_session):
    """Create a test client with mocked dependencies"""
    app = FastAPI()
    app.include_router(router)

    # Override the database dependency
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides = {"locavox.database.get_db_session": override_get_db}

    return TestClient(app)


class TestAuthEndpoints:
    """Test cases for authentication endpoints"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_db_session, mock_user):
        """Test successful login with valid credentials"""
        # Create a test client
        with TestClient(app) as client:
            # Arrange - patch the required dependencies
            with patch("locavox.database.get_db_session", return_value=mock_db_session):
                with patch(
                    "locavox.services.auth_service.authenticate_user",
                    return_value=mock_user,
                ):
                    with patch(
                        "locavox.services.auth_service.create_access_token",
                        return_value="test_token",
                    ):
                        # Act
                        response = client.post(
                            "/auth/token",
                            data={"username": "testuser", "password": "testpassword"},
                        )

                        # Assert
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["access_token"] == "test_token"
                        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_db_session):
        """Test login with invalid credentials"""
        # Create a test client
        with TestClient(app) as client:
            # Arrange
            with patch("locavox.database.get_db_session", return_value=mock_db_session):
                with patch(
                    "locavox.services.auth_service.authenticate_user", return_value=None
                ):
                    # Act
                    response = client.post(
                        "/auth/token",
                        data={"username": "testuser", "password": "wrongpassword"},
                    )

                    # Assert
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED
                    data = response.json()
                    assert "detail" in data
                    assert "Incorrect username or password" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, mock_db_session):
        """Test login with inactive user account"""
        # Arrange
        inactive_user = User(
            id="user-inactive",
            username="inactive",
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            hashed_password="hashed_password_here",
            is_active=False,  # This user is inactive
            is_superuser=False,  # Added missing field
            created_at=datetime.utcnow(),  # Added missing field
        )

        # Create a test client
        with TestClient(app) as client:
            with patch("locavox.database.get_db_session", return_value=mock_db_session):
                with patch(
                    "locavox.services.auth_service.authenticate_user",
                    return_value=inactive_user,
                ):
                    # Act
                    response = client.post(
                        "/auth/token",
                        data={"username": "inactive", "password": "testpassword"},
                    )

                    # Assert
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED
                    data = response.json()
                    assert "detail" in data
                    assert "User account is disabled" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_db_session, created_user):
        """Test successful user registration"""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
        }

        # Create a test client
        with TestClient(app) as client:
            # Use MonkeyPatch to avoid conflicts with other tests
            with patch(
                "locavox.routers.auth.get_db_session", return_value=mock_db_session
            ):
                with patch(
                    "locavox.routers.auth.create_user", return_value=created_user
                ):
                    # Act
                    response = client.post(
                        "/auth/register",
                        json=user_data,
                    )

                    # Assert
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["username"] == created_user.username
                    assert data["email"] == created_user.email
                    assert "first_name" in data
                    assert data["first_name"] == created_user.first_name
                    assert "last_name" in data
                    assert data["last_name"] == created_user.last_name
                    assert "password" not in data  # Ensure password is not returned
                    assert (
                        "hashed_password" not in data
                    )  # Ensure hashed password is not returned

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, mock_db_session):
        """Test user registration with duplicate email"""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
        }

        # Create a test client
        with TestClient(app) as client:
            with patch(
                "locavox.routers.auth.get_db_session", return_value=mock_db_session
            ):
                with patch(
                    "locavox.routers.auth.create_user",
                    side_effect=UserExistsError(
                        "User with email existing@example.com already exists"
                    ),
                ):
                    # Act
                    response = client.post(
                        "/auth/register",
                        json=user_data,
                    )

                    # Assert
                    assert response.status_code == status.HTTP_409_CONFLICT
                    data = response.json()
                    assert "detail" in data
                    assert "already exists" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, mock_user):
        """Test getting the current authenticated user"""
        # Override the dependency for this test
        from locavox.main import app

        # Store original overrides to restore later
        original_overrides = app.dependency_overrides.copy()

        # Set up our test override
        app.dependency_overrides[auth_service.get_current_user] = lambda: mock_user

        try:
            # Act
            response = client.get("/auth/me")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == mock_user.id
            assert data["username"] == mock_user.username
            assert data["email"] == mock_user.email
            assert "hashed_password" not in data  # Ensure password hash is not returned
        finally:
            # Restore original dependency overrides
            app.dependency_overrides = original_overrides

    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self):
        """Test getting current user without authentication"""
        # Create a test client
        with TestClient(app) as client:
            # Arrange
            with patch(
                "locavox.routers.auth.auth_service.get_current_user",
                side_effect=HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                ),
            ):
                # Act
                response = client.get("/auth/me")

                # Assert
                assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_login_form_validation(self):
        """Test login form validation"""
        # Arrange - Missing password field
        with TestClient(app) as client:
            # Act
            response = client.post(
                "/auth/token",
                data={"username": "testuser"},  # Missing password
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_validation(self):
        """Test registration data validation"""
        # Arrange - Missing required fields
        user_data = {
            "username": "newuser",
            # Missing email and password
        }

        with TestClient(app) as client:
            # Act
            response = client.post(
                "/auth/register",
                json=user_data,
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "detail" in data
            # Check that validation errors for email and password are present
            field_errors = [error["loc"][1] for error in data["detail"]]
            assert "email" in field_errors
            assert "password" in field_errors


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
