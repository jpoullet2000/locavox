import pytest
from httpx import AsyncClient
from ..locavox.main import app  # Updated import path
from ..locavox.services import message_service, auth_service  # Updated import path
from unittest.mock import patch, AsyncMock

# ...existing test code...


@pytest.mark.asyncio
async def test_delete_message_success():
    # Mock the dependencies
    message_mock = AsyncMock(user_id="test_user_id")

    with (
        patch.object(
            auth_service, "get_current_user", return_value=AsyncMock(id="test_user_id")
        ),
        patch.object(message_service, "get_message", return_value=message_mock),
        patch.object(message_service, "delete_message", return_value=True),
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/topics/test_topic/messages/test_message_id"
            )

            assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_message_not_found():
    # Mock the dependencies
    with (
        patch.object(
            auth_service, "get_current_user", return_value=AsyncMock(id="test_user_id")
        ),
        patch.object(message_service, "get_message", return_value=None),
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/topics/test_topic/messages/non_existent_id"
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_message_forbidden():
    # Mock the dependencies - different user_id to trigger forbidden error
    message_mock = AsyncMock(user_id="different_user_id")

    with (
        patch.object(
            auth_service, "get_current_user", return_value=AsyncMock(id="test_user_id")
        ),
        patch.object(message_service, "get_message", return_value=message_mock),
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/topics/test_topic/messages/test_message_id"
            )

            assert response.status_code == 403
            assert "only delete your own messages" in response.json()["detail"].lower()


# ...existing test code...
