from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import ReviewStatus
from app.models.finding import Finding
from app.models.review import Review
from app.models.ticket import Ticket
from app.schemas.review import ReviewSearchQuery


def compute_quality_score(findings: list[Finding]) -> int:
    """Helper to calculate quality score dynamically based on severity deductions."""
    deductions = {"critical": 20, "high": 15, "medium": 10, "low": 5, "info": 2}
    score = 100
    for f in findings:
        score -= deductions.get(f.severity.lower(), 5)
    return max(0, score)


class ReviewQueryRepository:
    async def get_metrics(self, db: AsyncSession) -> dict[str, Any]:
        """Aggregate high-level dashboard metrics for reviews."""
        # 1. Total reviews count
        total_result = await db.execute(select(func.count(Review.id)))
        reviews_count = total_result.scalar_one() or 0

        # 2. Completed reviews count
        completed_result = await db.execute(
            select(func.count(Review.id)).filter(
                Review.status == ReviewStatus.COMPLETED
            )
        )
        completed_reviews = completed_result.scalar_one() or 0

        # 3. Critical findings count
        critical_result = await db.execute(
            select(func.count(Finding.id)).filter(Finding.severity.ilike("critical"))
        )
        critical_findings = critical_result.scalar_one() or 0

        # 4. Language distribution
        lang_result = await db.execute(
            select(Review.language, func.count(Review.id)).group_by(Review.language)
        )
        language_distribution = {row[0]: row[1] for row in lang_result.all() if row[0]}

        # 5. Average Quality Score (calculated across completed reviews)
        completed_reviews_data = await db.execute(
            select(Review)
            .filter(Review.status == ReviewStatus.COMPLETED)
            .options(selectinload(Review.findings))
        )
        all_completed = completed_reviews_data.scalars().all()

        if all_completed:
            total_score = sum(compute_quality_score(r.findings) for r in all_completed)
            average_quality = round(total_score / len(all_completed), 1)
        else:
            average_quality = 100.0

        return {
            "reviews_count": reviews_count,
            "completed_reviews": completed_reviews,
            "critical_findings": critical_findings,
            "average_quality": average_quality,
            "language_distribution": language_distribution,
        }

    async def get_recent_reviews(
        self, db: AsyncSession, limit: int = 5
    ) -> list[Review]:
        """Retrieve recent reviews eagerly loading findings and tickets."""
        result = await db.execute(
            select(Review)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .options(selectinload(Review.findings).selectinload(Finding.ticket))
        )
        return list(result.scalars().all())

    async def get_review_with_findings_and_tickets(
        self, db: AsyncSession, review_id: int
    ) -> Review | None:
        """Fetch review details, eagerly loading findings and associated tickets."""
        result = await db.execute(
            select(Review)
            .filter(Review.id == review_id)
            .options(selectinload(Review.findings).selectinload(Finding.ticket))
        )
        return result.scalars().first()

    async def search(
        self, db: AsyncSession, query: ReviewSearchQuery
    ) -> tuple[list[tuple[Review, int]], int]:
        """Search, filter, sort, and paginate reviews."""
        # Start base statement
        stmt = select(Review).options(
            selectinload(Review.findings).selectinload(Finding.ticket)
        )

        # Filter by status
        if query.status:
            stmt = stmt.filter(Review.status == query.status)

        # Filter by language
        if query.language:
            stmt = stmt.filter(Review.language.ilike(query.language))

        # Filter critical findings presence
        if query.critical_only:
            stmt = stmt.filter(Review.findings.any(Finding.severity.ilike("critical")))

        # Filter by presence of tickets
        if query.has_tickets is not None:
            if query.has_tickets:
                stmt = stmt.filter(Review.findings.any(Finding.ticket.has()))
            else:
                stmt = stmt.filter(~Review.findings.any(Finding.ticket.has()))

        # Filter by search query
        if query.search:
            search_term = query.search.strip()
            conditions = [
                Review.language.ilike(f"%{search_term}%"),
                Review.findings.any(Finding.title.ilike(f"%{search_term}%")),
                Review.findings.any(Finding.description.ilike(f"%{search_term}%")),
                Review.findings.any(
                    Finding.ticket.has(Ticket.title.ilike(f"%{search_term}%"))
                ),
            ]
            if search_term.isdigit():
                conditions.append(Review.id == int(search_term))

            stmt = stmt.filter(or_(*conditions))

        # Execute query
        res = await db.execute(stmt)
        reviews = res.scalars().all()

        # Compute dynamic quality scores & filter by range
        processed = []
        for r in reviews:
            score = compute_quality_score(r.findings)
            if query.quality_min is not None and score < query.quality_min:
                continue
            if query.quality_max is not None and score > query.quality_max:
                continue
            processed.append((r, score))

        # Sort the results
        if query.sort_by == "oldest":
            processed.sort(key=lambda x: x[0].created_at)
        elif query.sort_by == "highest_quality":
            processed.sort(key=lambda x: (x[1], x[0].created_at), reverse=True)
        elif query.sort_by == "lowest_quality":
            processed.sort(key=lambda x: (x[1], -x[0].created_at.timestamp()))
        elif query.sort_by == "most_findings":
            processed.sort(key=lambda x: len(x[0].findings), reverse=True)
        elif query.sort_by == "least_findings":
            processed.sort(key=lambda x: len(x[0].findings))
        else:  # newest
            processed.sort(key=lambda x: x[0].created_at, reverse=True)

        # Paginate
        total = len(processed)
        start = (query.page - 1) * query.limit
        end = start + query.limit
        paginated_items = processed[start:end]

        return paginated_items, total


review_query_repository = ReviewQueryRepository()
