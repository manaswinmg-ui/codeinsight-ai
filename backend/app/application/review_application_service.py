"""
ReviewApplicationService — Application Layer (EPIC-07 ARCHITECTURE-01)

Responsibilities:
  - Receive review request use cases from the API layer
  - Coordinate ReviewService (domain) and ReviewProcessingService (domain)
  - Manage background task scheduling and session lifecycle
  - Compute presentation-level data (quality score, summary)
  - Assemble and return response schemas

Does NOT contain:
  - Business rules (those live in ReviewService / ReviewProcessingService)
  - HTTP concerns (those stay in the API endpoint)
  - Persistence logic (that lives in the repositories)
"""

import logging

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models.enums import ReviewStatus
from app.models.ticket import Ticket
from app.schemas.review import (
    FindingResponse,
    ReviewDetailResponse,
    ReviewListItemResponse,
    ReviewResponse,
)
from app.services.review_processing_service import (
    ReviewProcessingService,
    review_processing_service,
)
from app.services.review_service import ReviewService, review_service

logger = logging.getLogger("app.application.review")


class ReviewApplicationService:
    """
    Orchestrates the two core review use cases:

    1. submit_review  — create a new review and enqueue background processing
    2. get_review_detail — retrieve a completed review with findings and metrics

    Depends on:
        ReviewService           (domain — create/fetch/lifecycle)
        ReviewProcessingService (domain — AI pipeline execution)
    """

    def __init__(
        self,
        review_svc: ReviewService = review_service,
        processing_svc: ReviewProcessingService = review_processing_service,
    ) -> None:
        self._review_svc = review_svc
        self._processing_svc = processing_svc

    # ─────────────────────────────────────────────────────────────────────────
    # Use Case 1: Submit a new code review
    # ─────────────────────────────────────────────────────────────────────────

    async def submit_review(
        self,
        db: AsyncSession,
        *,
        code: str,
        language: str,
        background_tasks: BackgroundTasks,
        user_id: int | None = None,
    ) -> ReviewResponse:
        """
        Create a new review record in PENDING state and schedule AI processing.

        Workflow:
            1. Delegate creation + business validation to ReviewService
            2. Enqueue background processing task
            3. Return ReviewResponse DTO

        Raises:
            ValueError: propagated from ReviewService when input is invalid
        """
        review = await self._review_svc.create_review(
            db, code=code, language=language, user_id=user_id
        )
        background_tasks.add_task(self._run_processing_task, review.id)

        return ReviewResponse(
            review_id=review.id,
            status=review.status,
            created_at=review.created_at,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Use Case 2: List all past reviews (history sidebar)
    # ─────────────────────────────────────────────────────────────────────────

    async def list_reviews(self, db: AsyncSession) -> list[ReviewListItemResponse]:
        """Return a lightweight list of all reviews, ordered newest first."""
        reviews = await self._review_svc.list_reviews(db)
        return [
            ReviewListItemResponse(
                id=r.id,
                language=r.language,
                status=r.status,
                created_at=r.created_at,
            )
            for r in reviews
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # Use Case 3: Get review detail with findings and computed metrics
    # ─────────────────────────────────────────────────────────────────────────

    async def get_review_detail(
        self,
        db: AsyncSession,
        review_id: int,
    ) -> ReviewDetailResponse | None:
        """
        Retrieve a review with its findings, compute quality metrics, and assemble
        the full detail response.

        Returns None if the review does not exist (caller maps this to HTTP 404).

        Workflow:
            1. Fetch review + findings from ReviewService
            2. Compute quality score (severity-weighted deduction)
            3. Compute textual summary based on status
            4. Assemble and return ReviewDetailResponse DTO
        """
        review = await self._review_svc.get_review_with_findings(db, review_id)
        if not review:
            return None

        findings = review.findings or []
        finding_ids = [f.id for f in findings]

        # Batch query associated tickets to prevent N+1 lazy loading issues
        ticket_map = {}
        if finding_ids:
            result = await db.execute(
                select(Ticket.id, Ticket.finding_id).filter(
                    Ticket.finding_id.in_(finding_ids)
                )
            )
            for ticket_id, finding_id in result.all():
                ticket_map[finding_id] = ticket_id

        # ── Quality score: severity-weighted deduction ──────────────────────
        _deductions = {"critical": 20, "high": 15, "medium": 10, "low": 5, "info": 2}
        score = 100
        for f in findings:
            score -= _deductions.get(f.severity.lower(), 5)
        score = max(0, score)

        # ── Textual summary: derived from review status ─────────────────────
        status_name = (
            review.status.name if hasattr(review.status, "name") else str(review.status)
        )

        if status_name == ReviewStatus.COMPLETED:
            summary = f"Review completed with {len(findings)} finding(s) detected."
        elif status_name == ReviewStatus.FAILED:
            summary = "Review processing failed."
            score = 0
        else:
            summary = "Review analysis is currently in progress."
            score = 0

        # ── Assemble response DTO ───────────────────────────────────────────
        return ReviewDetailResponse(
            id=review.id,
            code=review.code,
            language=review.language,
            status=review.status,
            summary=summary,
            quality_score=score,
            findings=[
                FindingResponse(
                    id=f.id,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    status=f.status,
                    suggested_fix=f.suggested_fix,
                    test_case_hint=f.test_case_hint,
                    category=getattr(f, "category", None),
                    confidence=getattr(f, "confidence", None),
                    impact=getattr(f, "impact", None),
                    why_it_matters=getattr(f, "why_it_matters", None),
                    improved_code=getattr(f, "improved_code", None),
                    estimated_fix_time=getattr(f, "estimated_fix_time", None),
                    references=getattr(f, "references", None),
                    line_start=getattr(f, "line_start", None),
                    line_end=getattr(f, "line_end", None),
                    ticket_id=ticket_map.get(f.id),
                )
                for f in findings
            ],
            created_at=review.created_at,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Internal: Background task — manages its own DB session lifecycle
    # ─────────────────────────────────────────────────────────────────────────

    async def _run_processing_task(self, review_id: int) -> None:
        """
        Execute the AI review pipeline in the background.

        Opens a dedicated database session for the background task to avoid
        sharing a session across async context boundaries.
        """
        async with SessionLocal() as db:
            try:
                await self._processing_svc.process_review(db, review_id)
            except Exception as exc:
                logger.error(
                    "Background processing failed for review %d: %s",
                    review_id,
                    exc,
                    exc_info=True,
                )


# Module-level singleton — consistent with existing service singleton pattern
review_application_service = ReviewApplicationService()
