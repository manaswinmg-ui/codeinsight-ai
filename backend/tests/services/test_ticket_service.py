from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.enums import (
    FindingCategory,
    FindingStatus,
    TicketPriority,
    TicketStatus,
)
from app.models.finding import Finding
from app.models.ticket import Ticket
from app.services.ticket_service import (
    FindingNotFoundError,
    TicketAlreadyExistsError,
    TicketService,
)


@pytest.mark.asyncio
async def test_ticket_service_map_priority() -> None:
    service = TicketService(finding_repo=MagicMock(), ticket_repo=MagicMock())
    assert service.map_priority("CRITICAL") == TicketPriority.P0
    assert service.map_priority("HIGH") == TicketPriority.P1
    assert service.map_priority("MEDIUM") == TicketPriority.P2
    assert service.map_priority("LOW") == TicketPriority.P3
    assert service.map_priority("INFO") == TicketPriority.P3
    assert service.map_priority("UNKNOWN") == TicketPriority.P2


@pytest.mark.asyncio
async def test_create_ticket_from_finding_success() -> None:
    mock_finding = Finding(
        id=123,
        review_id=1,
        title="SQL Injection",
        description="SQL injection in queries.",
        severity="HIGH",
        status=FindingStatus.OPEN,
        category=FindingCategory.SECURITY,
    )

    mock_finding_repo = MagicMock()
    mock_finding_repo.get = AsyncMock(return_value=mock_finding)

    mock_ticket_repo = MagicMock()
    mock_ticket_repo.get_by_finding_id = AsyncMock(return_value=None)
    mock_ticket_repo.create = AsyncMock(side_effect=lambda db, ticket: ticket)

    service = TicketService(
        finding_repo=mock_finding_repo, ticket_repo=mock_ticket_repo
    )

    db = AsyncMock()
    ticket = await service.create_ticket_from_finding(db, 123)

    assert ticket.finding_id == 123
    assert ticket.title == "SQL Injection"
    assert ticket.description == "SQL injection in queries."
    assert ticket.priority == TicketPriority.P1
    assert ticket.status == TicketStatus.OPEN

    mock_finding_repo.get.assert_called_once_with(db, 123)
    mock_ticket_repo.get_by_finding_id.assert_called_once_with(db, 123)
    mock_ticket_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_ticket_from_finding_not_found() -> None:
    mock_finding_repo = MagicMock()
    mock_finding_repo.get = AsyncMock(return_value=None)

    mock_ticket_repo = MagicMock()

    service = TicketService(
        finding_repo=mock_finding_repo, ticket_repo=mock_ticket_repo
    )

    db = AsyncMock()
    with pytest.raises(FindingNotFoundError) as exc_info:
        await service.create_ticket_from_finding(db, 999)

    assert "Finding with ID 999 not found" in str(exc_info.value)
    mock_finding_repo.get.assert_called_once_with(db, 999)


@pytest.mark.asyncio
async def test_create_ticket_from_finding_already_exists() -> None:
    mock_finding = Finding(
        id=123,
        review_id=1,
        title="SQL Injection",
        description="SQL injection in queries.",
        severity="HIGH",
        status=FindingStatus.OPEN,
    )
    mock_ticket = Ticket(id=456, finding_id=123)

    mock_finding_repo = MagicMock()
    mock_finding_repo.get = AsyncMock(return_value=mock_finding)

    mock_ticket_repo = MagicMock()
    mock_ticket_repo.get_by_finding_id = AsyncMock(return_value=mock_ticket)

    service = TicketService(
        finding_repo=mock_finding_repo, ticket_repo=mock_ticket_repo
    )

    db = AsyncMock()
    with pytest.raises(TicketAlreadyExistsError) as exc_info:
        await service.create_ticket_from_finding(db, 123)

    assert "Ticket already exists for Finding 123" in str(exc_info.value)
    mock_finding_repo.get.assert_called_once_with(db, 123)
    mock_ticket_repo.get_by_finding_id.assert_called_once_with(db, 123)


@pytest.mark.asyncio
async def test_validate_and_update_status_success() -> None:
    mock_ticket = Ticket(
        id=456,
        finding_id=123,
        status=TicketStatus.OPEN,
    )
    mock_ticket_repo = MagicMock()
    mock_ticket_repo.get_by_id = AsyncMock(return_value=mock_ticket)

    service = TicketService(finding_repo=MagicMock(), ticket_repo=mock_ticket_repo)
    db = AsyncMock()
    db.add = MagicMock()

    updated = await service.validate_and_update_status(
        db, 456, TicketStatus.IN_PROGRESS
    )
    assert updated.status == TicketStatus.IN_PROGRESS
    assert updated.resolved_at is None


@pytest.mark.asyncio
async def test_validate_and_update_status_invalid_transition() -> None:
    from app.services.ticket_service import InvalidStatusTransitionError

    mock_ticket = Ticket(
        id=456,
        finding_id=123,
        status=TicketStatus.CLOSED,
    )
    mock_ticket_repo = MagicMock()
    mock_ticket_repo.get_by_id = AsyncMock(return_value=mock_ticket)

    service = TicketService(finding_repo=MagicMock(), ticket_repo=mock_ticket_repo)
    db = AsyncMock()

    with pytest.raises(InvalidStatusTransitionError) as exc_info:
        await service.validate_and_update_status(db, 456, TicketStatus.IN_PROGRESS)

    assert "Cannot transition from CLOSED to IN_PROGRESS" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_and_update_status_resolution_notes() -> None:
    mock_ticket = Ticket(
        id=456,
        finding_id=123,
        status=TicketStatus.IN_REVIEW,
    )
    mock_ticket_repo = MagicMock()
    mock_ticket_repo.get_by_id = AsyncMock(return_value=mock_ticket)

    service = TicketService(finding_repo=MagicMock(), ticket_repo=mock_ticket_repo)
    db = AsyncMock()
    db.add = MagicMock()

    updated = await service.validate_and_update_status(
        db,
        456,
        TicketStatus.DONE,
        resolution_notes="Fixed SQL injection using parameterized query",
    )
    assert updated.status == TicketStatus.DONE
    assert updated.resolved_at is not None
    assert updated.resolution_notes == "Fixed SQL injection using parameterized query"
