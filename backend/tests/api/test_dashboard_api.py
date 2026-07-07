from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.dashboard import DashboardMetrics, ReviewSummary, TicketSummary
from app.schemas.review import PaginatedResponse, ReviewComparisonResponse


@pytest.mark.asyncio
async def test_get_dashboard_metrics_api(client: AsyncClient) -> None:
    mock_metrics = DashboardMetrics(
        reviews_count=5,
        completed_reviews=4,
        open_tickets=2,
        critical_findings=1,
        average_quality=92.0,
        language_distribution={"python": 5}
    )

    with patch(
        "app.application.dashboard_application_service.DashboardApplicationService.get_dashboard_metrics",
        new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_metrics

        response = await client.get("/api/v1/dashboard/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["reviews_count"] == 5
        assert data["average_quality"] == 92.0
        assert data["language_distribution"] == {"python": 5}


@pytest.mark.asyncio
async def test_get_recent_reviews_api(client: AsyncClient) -> None:
    mock_item = ReviewSummary(
        id=1,
        language="python",
        status="COMPLETED",
        created_at=datetime.now(UTC),
        quality_score=95,
        findings_count=1,
        open_tickets_count=0
    )

    with patch(
        "app.application.dashboard_application_service.DashboardApplicationService.get_recent_reviews",
        new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [mock_item]

        response = await client.get("/api/v1/dashboard/recent-reviews?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["quality_score"] == 95


@pytest.mark.asyncio
async def test_get_recent_tickets_api(client: AsyncClient) -> None:
    mock_item = TicketSummary(
        id=1,
        priority="P2",
        status="OPEN",
        title="Unused import",
        review_id=10,
        created_at=datetime.now(UTC)
    )

    with patch(
        "app.application.dashboard_application_service.DashboardApplicationService.get_recent_tickets",
        new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [mock_item]

        response = await client.get("/api/v1/dashboard/recent-tickets?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["title"] == "Unused import"


@pytest.mark.asyncio
async def test_search_reviews_api(client: AsyncClient) -> None:
    mock_item = ReviewSummary(
        id=1,
        language="python",
        status="COMPLETED",
        created_at=datetime.now(UTC),
        quality_score=95,
        findings_count=1,
        open_tickets_count=0
    )
    mock_response = PaginatedResponse[ReviewSummary](
        items=[mock_item],
        total=1,
        page=1,
        limit=10,
        pages=1
    )

    with patch(
        "app.application.review_history_application_service.ReviewHistoryApplicationService.search_reviews",
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_response

        response = await client.get("/api/v1/reviews?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == 1


@pytest.mark.asyncio
async def test_compare_reviews_api(client: AsyncClient) -> None:
    mock_response = ReviewComparisonResponse(
        left_review_id=1,
        right_review_id=2,
        quality_difference=5,
        new_findings=[],
        resolved_findings=[],
        critical_fixed_count=0,
        tickets_closed_count=0
    )

    with patch(
        "app.application.review_history_application_service.ReviewHistoryApplicationService.compare_reviews",
        new_callable=AsyncMock
    ) as mock_compare:
        mock_compare.return_value = mock_response

        payload = {"left_review_id": 1, "right_review_id": 2}
        response = await client.post("/api/v1/reviews/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["quality_difference"] == 5
