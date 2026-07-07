from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.review_query_repository import (
    ReviewQueryRepository,
    compute_quality_score,
    review_query_repository,
)
from app.repositories.ticket_query_repository import (
    TicketQueryRepository,
    ticket_query_repository,
)
from app.schemas.dashboard import DashboardMetrics, ReviewSummary, TicketSummary


class DashboardApplicationService:
    def __init__(
        self,
        review_query_repo: ReviewQueryRepository = review_query_repository,
        ticket_query_repo: TicketQueryRepository = ticket_query_repository,
    ) -> None:
        self.review_query_repo = review_query_repo
        self.ticket_query_repo = ticket_query_repo

    async def get_dashboard_metrics(self, db: AsyncSession) -> DashboardMetrics:
        """Fetch aggregated metrics for the dashboard view."""
        rev_metrics = await self.review_query_repo.get_metrics(db)
        tkt_metrics = await self.ticket_query_repo.get_metrics(db)

        return DashboardMetrics(
            reviews_count=rev_metrics["reviews_count"],
            completed_reviews=rev_metrics["completed_reviews"],
            open_tickets=tkt_metrics["open_tickets"],
            critical_findings=rev_metrics["critical_findings"],
            average_quality=rev_metrics["average_quality"],
            language_distribution=rev_metrics["language_distribution"],
        )

    async def get_recent_reviews(
        self, db: AsyncSession, limit: int = 5
    ) -> list[ReviewSummary]:
        """Fetch the most recent reviews with dynamic quality and ticket metrics."""
        reviews = await self.review_query_repo.get_recent_reviews(db, limit)
        summaries = []
        for r in reviews:
            quality_score = compute_quality_score(r.findings)
            open_tickets_count = sum(
                1
                for f in r.findings
                if f.ticket and f.ticket.status.name not in ("DONE", "CLOSED")
            )
            summaries.append(
                ReviewSummary(
                    id=r.id,
                    language=r.language,
                    status=(
                        r.status.name if hasattr(r.status, "name") else str(r.status)
                    ),
                    created_at=r.created_at,
                    quality_score=quality_score,
                    findings_count=len(r.findings),
                    open_tickets_count=open_tickets_count,
                )
            )
        return summaries

    async def get_recent_tickets(
        self, db: AsyncSession, limit: int = 5
    ) -> list[TicketSummary]:
        """Fetch the most recent tickets with priority, status, and parent review ID."""
        tickets = await self.ticket_query_repo.get_recent_tickets(db, limit)
        summaries = []
        for t in tickets:
            summaries.append(
                TicketSummary(
                    id=t.id,
                    priority=(
                        t.priority.name
                        if hasattr(t.priority, "name")
                        else str(t.priority)
                    ),
                    status=(
                        t.status.name if hasattr(t.status, "name") else str(t.status)
                    ),
                    title=t.title,
                    review_id=t.finding.review_id if t.finding else 0,
                    created_at=t.created_at,
                )
            )
        return summaries


dashboard_application_service = DashboardApplicationService()
