from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.enums import ReviewStatus
from app.models.review import Review
from app.repositories.review_query_repository import ReviewQueryRepository
from app.schemas.review import ReviewSearchQuery


@pytest.mark.asyncio
async def test_get_metrics_success() -> None:
    # Arrange
    db = AsyncMock()

    # Mock return values for the 5 SQL executions in get_metrics
    res_total = MagicMock()
    res_total.scalar_one.return_value = 10

    res_completed = MagicMock()
    res_completed.scalar_one.return_value = 8

    res_critical = MagicMock()
    res_critical.scalar_one.return_value = 2

    res_lang = MagicMock()
    res_lang.all.return_value = [("python", 7), ("javascript", 3)]

    res_avg = MagicMock()
    res_avg.scalar_one.return_value = 84.5

    db.execute.side_effect = [res_total, res_completed, res_critical, res_lang, res_avg]

    repo = ReviewQueryRepository()

    # Act
    metrics = await repo.get_metrics(db)

    # Assert
    assert metrics["reviews_count"] == 10
    assert metrics["completed_reviews"] == 8
    assert metrics["critical_findings"] == 2
    assert metrics["average_quality"] == 84.5
    assert metrics["language_distribution"] == {"python": 7, "javascript": 3}
    assert db.execute.call_count == 5


@pytest.mark.asyncio
async def test_search_reviews_db_level() -> None:
    # Arrange
    db = AsyncMock()

    # Mock total count count_stmt
    res_count = MagicMock()
    res_count.scalar_one.return_value = 15

    # Mock paginated reviews return
    res_reviews = MagicMock()
    mock_review = Review(
        id=1,
        language="python",
        status=ReviewStatus.COMPLETED,
        quality_score=95,
        findings=[],
    )
    res_reviews.scalars.return_value.all.return_value = [mock_review]

    db.execute.side_effect = [res_count, res_reviews]

    repo = ReviewQueryRepository()
    query = ReviewSearchQuery(
        page=1, limit=10, quality_min=90, sort_by="highest_quality"
    )

    # Act
    processed, total = await repo.search(db, query)

    # Assert
    assert total == 15
    assert len(processed) == 1
    assert processed[0][0].id == 1
    assert processed[0][1] == 95
    assert db.execute.call_count == 2
