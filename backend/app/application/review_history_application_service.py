from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finding import Finding
from app.repositories.review_query_repository import (
    ReviewQueryRepository,
    compute_quality_score,
    review_query_repository,
)
from app.schemas.dashboard import ReviewSummary
from app.schemas.review import (
    FindingComparisonItem,
    PaginatedResponse,
    ReviewComparisonResponse,
    ReviewSearchQuery,
)


def findings_match(f1: Finding, f2: Finding) -> bool:
    """Determine if finding f1 matches finding f2 (meaning it is the same issue)."""
    t1 = f1.title.strip().lower()
    t2 = f2.title.strip().lower()
    l1 = f1.line_start
    l2 = f2.line_start

    # Exact title and line match
    if l1 is not None and l1 == l2:
        if t1 == t2:
            return True

    # Same line and description similarity (Jaccard index of words >= 0.4)
    if l1 is not None and l1 == l2:
        w1 = set(f1.description.lower().split())
        w2 = set(f2.description.lower().split())
        if w1 and w2:
            jaccard = len(w1.intersection(w2)) / len(w1.union(w2))
            if jaccard >= 0.4:
                return True

    # If both line numbers are missing, match by exact title
    if l1 is None and l2 is None and t1 == t2:
        return True

    return False


class ReviewHistoryApplicationService:
    def __init__(self, review_query_repo: ReviewQueryRepository = review_query_repository) -> None:
        self.review_query_repo = review_query_repo

    async def search_reviews(
        self, db: AsyncSession, query: ReviewSearchQuery
    ) -> PaginatedResponse[ReviewSummary]:
        """Search, filter, paginate, and sort reviews."""
        items_with_scores, total = await self.review_query_repo.search(db, query)
        summaries = []
        for r, score in items_with_scores:
            open_tickets_count = sum(
                1 for f in r.findings
                if f.ticket and f.ticket.status.name not in ("DONE", "CLOSED")
            )
            summaries.append(
                ReviewSummary(
                    id=r.id,
                    language=r.language,
                    status=r.status.name if hasattr(r.status, "name") else str(r.status),
                    created_at=r.created_at,
                    quality_score=score,
                    findings_count=len(r.findings),
                    open_tickets_count=open_tickets_count,
                )
            )
        pages = (total + query.limit - 1) // query.limit if query.limit > 0 else 1
        return PaginatedResponse(
            items=summaries,
            total=total,
            page=query.page,
            limit=query.limit,
            pages=pages,
        )

    async def compare_reviews(
        self, db: AsyncSession, left_id: int, right_id: int
    ) -> ReviewComparisonResponse:
        """Compare two reviews on quality, new findings, resolved findings, and ticket progress."""
        left_review = await self.review_query_repo.get_review_with_findings_and_tickets(db, left_id)
        right_review = await self.review_query_repo.get_review_with_findings_and_tickets(db, right_id)

        if not left_review or not right_review:
            raise ValueError("One or both reviews to compare could not be found.")

        left_findings = left_review.findings or []
        right_findings = right_review.findings or []

        left_score = compute_quality_score(left_findings)
        right_score = compute_quality_score(right_findings)
        quality_diff = right_score - left_score

        # Identify matches
        matched_right_ids = set()
        matched_left_ids = set()

        for lf in left_findings:
            for rf in right_findings:
                if rf.id not in matched_right_ids and findings_match(lf, rf):
                    matched_left_ids.add(lf.id)
                    matched_right_ids.add(rf.id)
                    break

        # Resolved findings are in left but not matched in right
        resolved_items = []
        critical_fixed = 0
        for lf in left_findings:
            if lf.id not in matched_left_ids:
                resolved_items.append(
                    FindingComparisonItem(
                        id=lf.id,
                        title=lf.title,
                        severity=lf.severity,
                        category=lf.category.name if hasattr(lf.category, "name") else str(lf.category or "UNKNOWN"),
                        line_start=lf.line_start,
                    )
                )
                if lf.severity.upper() == "CRITICAL":
                    critical_fixed += 1

        # New findings are in right but not matched in left
        new_items = []
        for rf in right_findings:
            if rf.id not in matched_right_ids:
                new_items.append(
                    FindingComparisonItem(
                        id=rf.id,
                        title=rf.title,
                        severity=rf.severity,
                        category=rf.category.name if hasattr(rf.category, "name") else str(rf.category or "UNKNOWN"),
                        line_start=rf.line_start,
                    )
                )

        # Count closed tickets from left review findings
        tickets_closed = sum(
            1 for lf in left_findings
            if lf.ticket and lf.ticket.status.name in ("DONE", "CLOSED")
        )

        return ReviewComparisonResponse(
            left_review_id=left_id,
            right_review_id=right_id,
            quality_difference=quality_diff,
            new_findings=new_items,
            resolved_findings=resolved_items,
            critical_fixed_count=critical_fixed,
            tickets_closed_count=tickets_closed,
        )


review_history_application_service = ReviewHistoryApplicationService()
