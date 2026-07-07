from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TicketStatus
from app.models.ticket import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self) -> None:
        super().__init__(Ticket)

    async def create(self, db: AsyncSession, *, ticket: Ticket) -> Ticket:
        """Persist a new Ticket record."""
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket

    async def get_by_id(self, db: AsyncSession, ticket_id: int) -> Ticket | None:
        """Retrieve a Ticket by its integer ID."""
        result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
        return result.scalars().first()

    async def get_by_finding_id(
        self, db: AsyncSession, finding_id: int
    ) -> Ticket | None:
        """Retrieve the Ticket associated with a given Finding ID."""
        result = await db.execute(
            select(Ticket).filter(Ticket.finding_id == finding_id)
        )
        return result.scalars().first()

    async def update_status(
        self, db: AsyncSession, ticket_id: int, status: TicketStatus
    ) -> Ticket | None:
        """Update the status of an existing Ticket."""
        ticket = await self.get_by_id(db, ticket_id)
        if not ticket:
            return None
        ticket.status = status
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket


ticket_repository = TicketRepository()
