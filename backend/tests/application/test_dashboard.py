from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dashboard_application_service import DashboardApplicationService
from app.models.enums import ReviewStatus, TicketPriority, TicketStatus
from app.models.finding import Finding
from app.models.review import Review
from app.models.ticket import Ticket


@pytest.mark.asyncio
async def test_get_dashboard_metrics_success() -> None:
    # Arrange
    mock_rev_repo = MagicMock()
    mock_tkt_repo = MagicMock()

    mock_rev_repo.get_metrics = AsyncMock(
        return_value={
            "reviews_count": 10,
            "completed_reviews": 8,
            "critical_findings": 2,
            "average_quality": 84.5,
            "language_distribution": {"python": 7, "javascript": 3},
        }
    )
    mock_tkt_repo.get_metrics = AsyncMock(return_value={"open_tickets": 4})

    service = DashboardApplicationService(
        review_query_repo=mock_rev_repo, ticket_query_repo=mock_tkt_repo
    )

    # Act
    db = AsyncMock()
    metrics = await service.get_dashboard_metrics(db)

    # Assert
    assert metrics.reviews_count == 10
    assert metrics.completed_reviews == 8
    assert metrics.open_tickets == 4
    assert metrics.critical_findings == 2
    assert metrics.average_quality == 84.5
    assert metrics.language_distribution == {"python": 7, "javascript": 3}


@pytest.mark.asyncio
async def test_get_recent_reviews_success() -> None:
    # Arrange
    mock_rev_repo = MagicMock()
    mock_tkt_repo = MagicMock()

    # Mock Findings & Review
    f1 = Finding(
        id=1, title="Issue 1", description="desc", severity="critical", status="OPEN"
    )
    f2 = Finding(
        id=2, title="Issue 2", description="desc", severity="low", status="OPEN"
    )

    # Mock ticket for f1
    t1 = Ticket(
        id=10,
        priority=TicketPriority.P1,
        status=TicketStatus.OPEN,
        title="Ticket title",
        created_at=datetime.now(UTC),
    )
    f1.ticket = t1

    r1 = Review(
        id=101,
        language="python",
        status=ReviewStatus.COMPLETED,
        findings=[f1, f2],
        created_at=datetime.now(UTC),
    )

    mock_rev_repo.get_recent_reviews = AsyncMock(return_value=[r1])

    service = DashboardApplicationService(
        review_query_repo=mock_rev_repo, ticket_query_repo=mock_tkt_repo
    )

    # Act
    db = AsyncMock()
    summaries = await service.get_recent_reviews(db, limit=5)

    # Assert
    assert len(summaries) == 1
    s = summaries[0]
    assert s.id == 101
    assert s.language == "python"
    assert s.status == "COMPLETED"
    assert s.quality_score == 75  # 100 - 20 (critical) - 5 (low)
    assert s.findings_count == 2
    assert s.open_tickets_count == 1  # t1 is OPEN


@pytest.mark.asyncio
async def test_get_recent_tickets_success() -> None:
    # Arrange
    mock_rev_repo = MagicMock()
    mock_tkt_repo = MagicMock()

    f = Finding(id=1, review_id=101)
    t = Ticket(
        id=50,
        priority=TicketPriority.P2,
        status=TicketStatus.OPEN,
        title="SQL Injection",
        finding=f,
        created_at=datetime.now(UTC),
    )

    mock_tkt_repo.get_recent_tickets = AsyncMock(return_value=[t])

    service = DashboardApplicationService(
        review_query_repo=mock_rev_repo, ticket_query_repo=mock_tkt_repo
    )

    # Act
    db = AsyncMock()
    summaries = await service.get_recent_tickets(db, limit=5)

    # Assert
    assert len(summaries) == 1
    s = summaries[0]
    assert s.id == 50
    assert s.priority == "P2"
    assert s.status == "OPEN"
    assert s.title == "SQL Injection"
    assert s.review_id == 101
