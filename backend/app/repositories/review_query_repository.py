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

        # 5. Average Quality Score (calculated across completed reviews in SQL)
        avg_result = await db.execute(
            select(func.avg(Review.quality_score)).filter(
                Review.status == ReviewStatus.COMPLETED
            )
        )
        avg_val = avg_result.scalar_one()
        average_quality = round(float(avg_val), 1) if avg_val is not None else 100.0

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
        """Search, filter, sort, and paginate reviews in SQL."""
        # 1. Collect filter conditions
        filters = []
        if query.status:
            filters.append(Review.status == query.status)

        if query.language:
            filters.append(Review.language.ilike(query.language))

        if query.quality_min is not None:
            filters.append(Review.quality_score >= query.quality_min)

        if query.quality_max is not None:
            filters.append(Review.quality_score <= query.quality_max)

        if query.critical_only:
            filters.append(Review.findings.any(Finding.severity.ilike("critical")))

        if query.has_tickets is not None:
            if query.has_tickets:
                filters.append(Review.findings.any(Finding.ticket.has()))
            else:
                filters.append(~Review.findings.any(Finding.ticket.has()))

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

            filters.append(or_(*conditions))

        # 2. Get total matching count
        count_stmt = select(func.count(Review.id))
        if filters:
            count_stmt = count_stmt.filter(*filters)
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        # 3. Build query with sorting and pagination
        stmt = select(Review).options(
            selectinload(Review.findings).selectinload(Finding.ticket)
        )
        if filters:
            stmt = stmt.filter(*filters)

        # Apply sorting
        if query.sort_by == "oldest":
            stmt = stmt.order_by(Review.created_at.asc())
        elif query.sort_by == "highest_quality":
            stmt = stmt.order_by(Review.quality_score.desc(), Review.created_at.desc())
        elif query.sort_by == "lowest_quality":
            stmt = stmt.order_by(Review.quality_score.asc(), Review.created_at.desc())
        elif query.sort_by == "most_findings":
            subq = (
                select(
                    Finding.review_id, func.count(Finding.id).label("findings_count")
                )
                .group_by(Finding.review_id)
                .subquery()
            )
            stmt = stmt.outerjoin(subq, Review.id == subq.c.review_id).order_by(
                func.coalesce(subq.c.findings_count, 0).desc(), Review.created_at.desc()
            )
        elif query.sort_by == "least_findings":
            subq = (
                select(
                    Finding.review_id, func.count(Finding.id).label("findings_count")
                )
                .group_by(Finding.review_id)
                .subquery()
            )
            stmt = stmt.outerjoin(subq, Review.id == subq.c.review_id).order_by(
                func.coalesce(subq.c.findings_count, 0).asc(), Review.created_at.desc()
            )
        else:  # newest
            stmt = stmt.order_by(Review.created_at.desc())

        # Apply pagination
        stmt = stmt.offset((query.page - 1) * query.limit).limit(query.limit)

        res = await db.execute(stmt)
        reviews = res.scalars().all()

        processed = []
        for r in reviews:
            score = r.quality_score
            if score is None:
                score = compute_quality_score(r.findings)
            if r.status == ReviewStatus.FAILED:
                score = 0
            processed.append((r, score))

        return processed, total


review_query_repository = ReviewQueryRepository()
