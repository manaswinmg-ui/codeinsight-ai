from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.models.enums import ReviewStatus
from app.models.finding import Finding  # noqa: F401
from app.models.review import Review


@pytest.mark.asyncio
async def test_submit_code_review_success(client: AsyncClient) -> None:
    """Test successful code review submission."""
    mock_review = Review(
        id=123,
        code="def hello():\n    pass",
        language="python",
        status=ReviewStatus.PENDING,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "app.application.review_application_service.ReviewService.create_review",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.return_value = mock_review

        payload = {"code": "def hello():\n    pass", "language": "python"}
        response = await client.post("/api/v1/reviews", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["review_id"] == 123
        assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_submit_code_review_validation_empty_code(client: AsyncClient) -> None:
    """Test submission fails validation when code is empty."""
    payload = {"code": "", "language": "python"}
    response = await client.post("/api/v1/reviews", json=payload)
    # ValueError is mapped to HTTP 400 Bad Request
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_submit_code_review_validation_empty_lang(client: AsyncClient) -> None:
    """Test submission fails validation when language is empty."""
    payload = {"code": "print('hello')", "language": ""}
    response = await client.post("/api/v1/reviews", json=payload)
    # ValueError is mapped to HTTP 400 Bad Request
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_review_details_success(client: AsyncClient) -> None:
    """Test successful retrieval of code review details and findings."""
    from app.models.finding import Finding
    from app.models.enums import FindingStatus

    mock_findings = [
        Finding(
            id=1,
            review_id=123,
            title="Test Finding",
            description="Test Description",
            severity="medium",
            status=FindingStatus.OPEN,
            suggested_fix="print('fix')",
            test_case_hint="test boundary",
        )
    ]
    mock_review = Review(
        id=123,
        code="def hello():\n    pass",
        language="python",
        status=ReviewStatus.COMPLETED,
        findings=mock_findings,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "app.application.review_application_service.ReviewService.get_review_with_findings",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_review

        response = await client.get("/api/v1/reviews/123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["status"] == "COMPLETED"
        assert data["quality_score"] == 90  # 100 - 10 (medium severity deduction)
        assert len(data["findings"]) == 1
        assert data["findings"][0]["title"] == "Test Finding"
        assert data["findings"][0]["suggested_fix"] == "print('fix')"


@pytest.mark.asyncio
async def test_get_review_details_not_found(client: AsyncClient) -> None:
    """Test retrieval returns 404 if review does not exist."""
    with patch(
        "app.application.review_application_service.ReviewService.get_review_with_findings",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None

        response = await client.get("/api/v1/reviews/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"
