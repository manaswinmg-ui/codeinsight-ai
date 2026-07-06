from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TicketStatus
from app.repositories.ticket_repository import TicketRepository, ticket_repository
from app.schemas.ticket import TicketResponse
from app.services.ticket_service import TicketService, ticket_service


class TicketApplicationService:
    """
    Application layer orchestration service for Ticket use cases.
    Coordinates Domain Services and Repositories, converts and returns DTO response schemas.
    """

    def __init__(
        self,
        ticket_svc: TicketService = ticket_service,
        ticket_repo: TicketRepository = ticket_repository,
    ) -> None:
        self._ticket_svc = ticket_svc
        self._ticket_repo = ticket_repo

    async def create_ticket(
        self, db: AsyncSession, finding_id: int
    ) -> TicketResponse:
        """
        Orchestrate ticket creation from a finding.
        """
        ticket = await self._ticket_svc.create_ticket_from_finding(db, finding_id)
        return TicketResponse.model_validate(ticket)

    async def get_ticket(
        self, db: AsyncSession, ticket_id: int
    ) -> TicketResponse | None:
        """
        Orchestrate ticket retrieval by ID.
        """
        ticket = await self._ticket_repo.get_by_id(db, ticket_id)
        if not ticket:
            return None
        return TicketResponse.model_validate(ticket)

    async def update_ticket_status(
        self,
        db: AsyncSession,
        ticket_id: int,
        new_status: TicketStatus,
        resolution_notes: str | None = None,
    ) -> TicketResponse:
        """
        Orchestrate ticket status transition with validation.
        """
        ticket = await self._ticket_svc.validate_and_update_status(
            db, ticket_id, new_status, resolution_notes
        )
        return TicketResponse.model_validate(ticket)


ticket_application_service = TicketApplicationService()
