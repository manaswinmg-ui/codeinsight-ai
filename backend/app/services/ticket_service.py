import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TicketPriority, TicketStatus
from app.models.ticket import Ticket
from app.repositories.finding_repository import FindingRepository, finding_repository
from app.repositories.ticket_repository import TicketRepository, ticket_repository

logger = logging.getLogger("app.services.ticket")


class FindingNotFoundError(ValueError):
    """Raised when the requested Finding is not found in the repository."""

    pass


class TicketAlreadyExistsError(ValueError):
    """Raised when a ticket is already linked to the Finding."""

    pass


class InvalidStatusTransitionError(ValueError):
    """Raised when a ticket status transition is not allowed."""

    pass


class TicketNotFoundError(ValueError):
    """Raised when the requested Ticket is not found in the repository."""

    pass


# Allowed status transitions map
ALLOWED_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.OPEN: {TicketStatus.TODO, TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.TODO: {TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.IN_PROGRESS: {TicketStatus.IN_REVIEW, TicketStatus.TODO, TicketStatus.CLOSED},
    TicketStatus.IN_REVIEW: {TicketStatus.DONE, TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.DONE: {TicketStatus.CLOSED, TicketStatus.IN_PROGRESS},
    TicketStatus.CLOSED: set(),  # Terminal state
}


class TicketService:
    """
    Domain service for Ticket logic, validations, and mapping.
    """

    def __init__(
        self,
        finding_repo: FindingRepository = finding_repository,
        ticket_repo: TicketRepository = ticket_repository,
    ) -> None:
        self._finding_repo = finding_repo
        self._ticket_repo = ticket_repo

    def map_priority(self, severity: str) -> TicketPriority:
        """
        Map Finding severity to Ticket priority automatically:
            CRITICAL -> P0
            HIGH     -> P1
            MEDIUM   -> P2
            LOW      -> P3
            INFO     -> P3
        """
        sev = severity.strip().upper()
        if sev == "CRITICAL":
            return TicketPriority.P0
        elif sev == "HIGH":
            return TicketPriority.P1
        elif sev == "MEDIUM":
            return TicketPriority.P2
        elif sev in ("LOW", "INFO"):
            return TicketPriority.P3
        return TicketPriority.P2

    async def create_ticket_from_finding(
        self, db: AsyncSession, finding_id: int
    ) -> Ticket:
        """
        Domain logic to create a new ticket from an AI Finding.

        Validates:
            1. The finding exists
            2. The finding does not already have a ticket linked
        """
        # 1. Validate finding exists
        finding = await self._finding_repo.get(db, finding_id)
        if not finding:
            raise FindingNotFoundError(f"Finding with ID {finding_id} not found")

        # 2. Ensure finding has no existing ticket
        existing_ticket = await self._ticket_repo.get_by_finding_id(db, finding_id)
        if existing_ticket:
            raise TicketAlreadyExistsError(
                f"Ticket already exists for Finding {finding_id}"
            )

        # 3. Map severity to priority
        priority = self.map_priority(finding.severity)

        # 4. Instantiate Ticket
        ticket = Ticket(
            finding_id=finding.id,
            title=finding.title,
            description=finding.description,
            priority=priority,
            status=TicketStatus.OPEN,
        )

        # 5. Persist Ticket
        logger.info(
            "Creating ticket for finding %d with priority %s",
            finding_id,
            priority,
        )
        return await self._ticket_repo.create(db, ticket=ticket)

    async def validate_and_update_status(
        self,
        db: AsyncSession,
        ticket_id: int,
        new_status: TicketStatus,
        resolution_notes: str | None = None,
    ) -> Ticket:
        """
        Validate a status transition and update the ticket.

        Enforces the ALLOWED_TRANSITIONS map and auto-sets
        resolved_at when transitioning to DONE or CLOSED.
        """
        ticket = await self._ticket_repo.get_by_id(db, ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")

        current_status = TicketStatus(ticket.status)
        allowed = ALLOWED_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                f"Cannot transition from {current_status} to {new_status}. "
                f"Allowed: {', '.join(str(s) for s in allowed) or 'none (terminal state)'}"
            )

        ticket.status = new_status

        # Auto-set resolved_at and resolution_notes for terminal-like states
        if new_status in (TicketStatus.DONE, TicketStatus.CLOSED):
            ticket.resolved_at = datetime.now(timezone.utc)
            if resolution_notes:
                ticket.resolution_notes = resolution_notes
        else:
            # Clear resolved_at if reopening
            ticket.resolved_at = None

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        logger.info(
            "Ticket %d transitioned: %s -> %s",
            ticket_id,
            current_status,
            new_status,
        )
        return ticket


ticket_service = TicketService()
