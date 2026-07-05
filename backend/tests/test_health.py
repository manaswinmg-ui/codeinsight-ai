import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test the root index endpoint returns welcome message."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to CodeInsight AI API" in data["message"]
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient) -> None:
    """Test the health check endpoint returns 200 and healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert data["services"] == "healthy"
