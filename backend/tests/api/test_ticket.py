from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.models.enums import TicketPriority, TicketStatus
from app.schemas.ticket import TicketResponse


@pytest.mark.asyncio
async def test_create_ticket_success(client: AsyncClient) -> None:
    """Test successful creation of a bug ticket from a finding."""
    mock_ticket = TicketResponse(
        id=456,
        finding_id=123,
        title="SQL Injection Vulnerability",
        description="A potential SQL injection was found in raw execute statement.",
        priority=TicketPriority.P1,
        status=TicketStatus.OPEN,
        assignee=None,
        created_by=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        resolved_at=None,
        resolution_notes=None,
    )

    with patch(
        "app.application.ticket_application_service.TicketApplicationService.create_ticket",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.return_value = mock_ticket

        response = await client.post("/api/v1/findings/123/ticket")
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 456
        assert data["finding_id"] == 123
        assert data["title"] == "SQL Injection Vulnerability"
        assert data["priority"] == "P1"
        assert data["status"] == "OPEN"


@pytest.mark.asyncio
async def test_create_ticket_finding_not_found(client: AsyncClient) -> None:
    """Test that ticket creation returns 404 if finding does not exist."""
    from app.services.ticket_service import FindingNotFoundError

    with patch(
        "app.application.ticket_application_service.TicketApplicationService.create_ticket",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.side_effect = FindingNotFoundError("Finding with ID 999 not found")

        response = await client.post("/api/v1/findings/999/ticket")
        assert response.status_code == 404
        assert response.json()["detail"] == "Finding with ID 999 not found"


@pytest.mark.asyncio
async def test_create_ticket_already_exists(client: AsyncClient) -> None:
    """Test that ticket creation returns 409 if a ticket is already linked."""
    from app.services.ticket_service import TicketAlreadyExistsError

    with patch(
        "app.application.ticket_application_service.TicketApplicationService.create_ticket",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.side_effect = TicketAlreadyExistsError(
            "Ticket already exists for Finding 123"
        )

        response = await client.post("/api/v1/findings/123/ticket")
        assert response.status_code == 409
        assert response.json()["detail"] == "Ticket already exists for Finding 123"


@pytest.mark.asyncio
async def test_get_ticket_details_success(client: AsyncClient) -> None:
    """Test successful retrieval of ticket details."""
    mock_ticket = TicketResponse(
        id=456,
        finding_id=123,
        title="SQL Injection Vulnerability",
        description="A potential SQL injection was found in raw execute statement.",
        priority=TicketPriority.P1,
        status=TicketStatus.OPEN,
        assignee=None,
        created_by=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        resolved_at=None,
        resolution_notes=None,
    )

    with patch(
        "app.application.ticket_application_service.TicketApplicationService.get_ticket",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_ticket

        response = await client.get("/api/v1/tickets/456")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 456
        assert data["title"] == "SQL Injection Vulnerability"
        assert data["priority"] == "P1"
        assert data["status"] == "OPEN"


@pytest.mark.asyncio
async def test_get_ticket_details_not_found(client: AsyncClient) -> None:
    """Test that ticket details retrieval returns 404 if ticket does not exist."""
    with patch(
        "app.application.ticket_application_service.TicketApplicationService.get_ticket",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None

        response = await client.get("/api/v1/tickets/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Ticket not found"


@pytest.mark.asyncio
async def test_update_ticket_status_success(client: AsyncClient) -> None:
    mock_ticket = TicketResponse(
        id=456,
        finding_id=123,
        title="SQL Injection Vulnerability",
        description="A potential SQL injection was found in raw execute statement.",
        priority=TicketPriority.P1,
        status=TicketStatus.IN_PROGRESS,
        assignee=None,
        created_by=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        resolved_at=None,
        resolution_notes=None,
    )

    with patch(
        "app.application.ticket_application_service.TicketApplicationService.update_ticket_status",
        new_callable=AsyncMock,
    ) as mock_update:
        mock_update.return_value = mock_ticket

        response = await client.patch(
            "/api/v1/tickets/456/status",
            json={"status": "IN_PROGRESS", "resolution_notes": None},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_update_ticket_status_invalid_transition(client: AsyncClient) -> None:
    from app.services.ticket_service import InvalidStatusTransitionError

    with patch(
        "app.application.ticket_application_service.TicketApplicationService.update_ticket_status",
        new_callable=AsyncMock,
    ) as mock_update:
        mock_update.side_effect = InvalidStatusTransitionError(
            "Cannot transition from CLOSED to IN_PROGRESS"
        )

        response = await client.patch(
            "/api/v1/tickets/456/status",
            json={"status": "IN_PROGRESS"},
        )
        assert response.status_code == 422
        assert (
            "Cannot transition from CLOSED to IN_PROGRESS" in response.json()["detail"]
        )
