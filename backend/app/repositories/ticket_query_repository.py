from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import TicketStatus
from app.models.finding import Finding
from app.models.ticket import Ticket


class TicketQueryRepository:
    async def get_metrics(self, db: AsyncSession) -> dict[str, int]:
        """Get open tickets count for dashboard aggregation."""
        result = await db.execute(
            select(func.count(Ticket.id)).filter(
                and_(
                    Ticket.status != TicketStatus.DONE,
                    Ticket.status != TicketStatus.CLOSED,
                )
            )
        )
        open_count = result.scalar_one() or 0
        return {"open_tickets": open_count}

    async def get_recent_tickets(
        self, db: AsyncSession, limit: int = 5
    ) -> list[Ticket]:
        """Retrieve recent tickets, eagerly loading finding and review relationships."""
        result = await db.execute(
            select(Ticket)
            .order_by(Ticket.created_at.desc())
            .limit(limit)
            .options(selectinload(Ticket.finding).selectinload(Finding.review))
        )
        return list(result.scalars().all())

    async def search_tickets(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        status: TicketStatus | None = None,
    ) -> tuple[list[Ticket], int]:
        """Fetch a paginated list of tickets, optionally filtered by status."""
        # Total count query
        count_stmt = select(func.count(Ticket.id))
        if status:
            count_stmt = count_stmt.filter(Ticket.status == status)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one() or 0

        # Paginated query
        stmt = (
            select(Ticket)
            .options(selectinload(Ticket.finding).selectinload(Finding.review))
            .order_by(Ticket.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total


ticket_query_repository = TicketQueryRepository()
