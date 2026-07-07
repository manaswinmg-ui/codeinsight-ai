from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_api_register_success(client: AsyncClient) -> None:
    mock_user = User(
        id=1,
        username="jane_doe",
        email="jane@example.com",
        full_name="Jane Doe",
        is_active=True,
        is_superuser=False,
    )

    with patch(
        "app.application.auth_application_service.auth_application_service._auth_svc.register",
        new_callable=AsyncMock,
    ) as mock_reg:
        mock_reg.return_value = (mock_user, "access_token_123", "refresh_token_123")

        payload = {
            "username": "jane_doe",
            "email": "jane@example.com",
            "password": "Password123!",
            "full_name": "Jane Doe",
        }
        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["access_token"] == "access_token_123"
        assert data["refresh_token"] == "refresh_token_123"
        assert data["user"]["username"] == "jane_doe"
        assert data["user"]["email"] == "jane@example.com"


@pytest.mark.asyncio
async def test_api_login_success(client: AsyncClient) -> None:
    mock_user = User(
        id=1,
        username="jane_doe",
        email="jane@example.com",
        is_active=True,
    )

    with patch(
        "app.application.auth_application_service.auth_application_service._auth_svc.authenticate",
        new_callable=AsyncMock,
    ) as mock_auth:
        mock_auth.return_value = (mock_user, "access_token_123", "refresh_token_123")

        payload = {
            "email": "jane@example.com",
            "password": "Password123!",
        }
        response = await client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access_token_123"
        assert data["user"]["username"] == "jane_doe"


@pytest.mark.asyncio
async def test_api_refresh_success(client: AsyncClient) -> None:
    with patch(
        "app.application.auth_application_service.auth_application_service._auth_svc.refresh_access_token",
        new_callable=AsyncMock,
    ) as mock_refresh:
        mock_refresh.return_value = "new_access_token_abc"

        payload = {
            "refresh_token": "valid_refresh_token",
        }
        response = await client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token_abc"


@pytest.mark.asyncio
async def test_api_get_me_unauthorized(client: AsyncClient) -> None:
    # No auth header -> 401
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_api_get_me_success(client: AsyncClient, db_session: AsyncMock) -> None:
    from datetime import UTC, datetime
    mock_user = User(
        id=42,
        username="test_me",
        email="me@example.com",
        full_name="Test Me",
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "app.auth.dependencies.token_service.decode_access_token",
        return_value=42,
    ), patch(
        "app.auth.dependencies.user_repository.get",
        new_callable=AsyncMock,
    ) as mock_get_user:
        mock_get_user.return_value = mock_user

        headers = {"Authorization": "Bearer valid_access_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 42
        assert data["username"] == "test_me"
        assert data["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_api_logout_success(client: AsyncClient) -> None:
    mock_user = User(
        id=42,
        username="test_me",
        email="me@example.com",
        is_active=True,
    )

    with patch(
        "app.auth.dependencies.token_service.decode_access_token",
        return_value=42,
    ), patch(
        "app.auth.dependencies.user_repository.get",
        new_callable=AsyncMock,
    ) as mock_get_user:
        mock_get_user.return_value = mock_user

        headers = {"Authorization": "Bearer valid_access_token"}
        response = await client.post("/api/v1/auth/logout", headers=headers)

        assert response.status_code == 200
        assert response.json() == {"message": "Successfully logged out"}
