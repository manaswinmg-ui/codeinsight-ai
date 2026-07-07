from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.review_history_application_service import (
    ReviewHistoryApplicationService,
)
from app.models.enums import ReviewStatus, TicketPriority, TicketStatus
from app.models.finding import Finding
from app.models.review import Review
from app.models.ticket import Ticket
from app.schemas.review import ReviewSearchQuery


@pytest.mark.asyncio
async def test_search_reviews_success() -> None:
    # Arrange
    mock_rev_repo = MagicMock()

    r = Review(
        id=1,
        language="python",
        status=ReviewStatus.COMPLETED,
        findings=[],
        created_at=datetime.now(UTC)
    )

    mock_rev_repo.search = AsyncMock(return_value=([(r, 100)], 1))
    service = ReviewHistoryApplicationService(review_query_repo=mock_rev_repo)

    # Act
    db = AsyncMock()
    query = ReviewSearchQuery(page=1, limit=10)
    res = await service.search_reviews(db, query)

    # Assert
    assert res.total == 1
    assert len(res.items) == 1
    assert res.items[0].id == 1
    assert res.items[0].quality_score == 100
    assert res.items[0].findings_count == 0


@pytest.mark.asyncio
async def test_compare_reviews_success() -> None:
    # Arrange
    mock_rev_repo = MagicMock()

    # Left Review (older): findings are f1, f2
    f1 = Finding(id=10, review_id=1, title="SQL Injection", description="Raw SQL execution", severity="critical", line_start=15)
    f2 = Finding(id=11, review_id=1, title="Unused import", description="import os is unused", severity="low", line_start=2)

    # Simulate an open ticket for left finding f1
    t1 = Ticket(id=20, priority=TicketPriority.P1, status=TicketStatus.OPEN, finding=f1)
    f1.ticket = t1

    left_review = Review(id=1, findings=[f1, f2])

    # Right Review (newer): f1 is resolved (not present), f2 is still present (unused import), and f3 is newly added
    # We will map matching using lines and descriptions
    f2_new = Finding(id=12, review_id=2, title="Unused import", description="import os is unused", severity="low", line_start=2)
    f3 = Finding(id=13, review_id=2, title="Hardcoded Password", description="Password is exposed", severity="high", line_start=30)

    right_review = Review(id=2, findings=[f2_new, f3])

    mock_rev_repo.get_review_with_findings_and_tickets = AsyncMock(side_effect=lambda db, rid: left_review if rid == 1 else right_review)
    service = ReviewHistoryApplicationService(review_query_repo=mock_rev_repo)

    # Act
    db = AsyncMock()
    res = await service.compare_reviews(db, left_id=1, right_id=2)

    # Assert
    assert res.left_review_id == 1
    assert res.right_review_id == 2

    # Left quality score: 100 - 20 (critical) - 5 (low) = 75
    # Right quality score: 100 - 5 (low) - 15 (high) = 80
    assert res.quality_difference == 5

    # f1 (SQL Injection) should be resolved
    assert len(res.resolved_findings) == 1
    assert res.resolved_findings[0].title == "SQL Injection"
    assert res.critical_fixed_count == 1

    # f3 (Hardcoded Password) should be new
    assert len(res.new_findings) == 1
    assert res.new_findings[0].title == "Hardcoded Password"

    # No closed tickets on left review findings in left review (t1 was still OPEN)
    assert res.tickets_closed_count == 0
