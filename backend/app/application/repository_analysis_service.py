import asyncio
import logging
from datetime import UTC, datetime

from fastapi import BackgroundTasks
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models.enums import ReviewStatus
from app.models.finding import Finding
from app.models.repository import FileReview, Repository
from app.models.review import Review
from app.repository.repository_scanner import RepositoryScanner
from app.repository.repository_summary import RepositorySummary
from app.schemas.repository import (
    FileReviewResponse,
    RepositoryDetailResponse,
    RepositoryResponse,
)
from app.services.review_processing_service import (
    ReviewProcessingService,
    review_processing_service,
)

logger = logging.getLogger("app.application.repository_analysis")


class RepositoryAnalysisService:
    """Orchestrates multi-file repository reviews, parallel scanning, and quality metrics aggregation."""

    def __init__(self, processing_svc: ReviewProcessingService = review_processing_service) -> None:
        self.processing_svc = processing_svc

    async def submit_repository(
        self,
        db: AsyncSession,
        *,
        name: str,
        file_bytes: bytes,
        background_tasks: BackgroundTasks,
        user_id: int | None = None,
    ) -> RepositoryResponse:
        """
        Scan zip in memory, validate limits, create DB entities, and enqueue parallel analysis.
        """
        # 1. Scan ZIP and run limits validation
        scanned_files = RepositoryScanner.scan_zip(file_bytes)
        if not scanned_files:
            raise ValueError("No supported source code files found in the ZIP archive.")

        # 2. Create Repository in PENDING status
        repo = Repository(name=name, status=ReviewStatus.PENDING, user_id=user_id)
        db.add(repo)
        await db.flush()  # Get repo.id

        # 3. Create individual Review and FileReview rows
        for sf in scanned_files:
            review = Review(
                code=sf["content"],
                language=sf["language"],
                status=ReviewStatus.PENDING
            )
            db.add(review)
            await db.flush()  # Get review.id

            file_rev = FileReview(
                repository_id=repo.id,
                review_id=review.id,
                file_path=sf["path"],
                size_bytes=sf["size_bytes"]
            )
            db.add(file_rev)

        await db.commit()
        await db.refresh(repo)

        # 4. Enqueue background task
        background_tasks.add_task(self._run_repository_analysis_task, repo.id)

        return RepositoryResponse(
            repository_id=repo.id,
            status=repo.status,
            created_at=repo.created_at
        )

    async def get_repository_detail(self, db: AsyncSession, repo_id: int) -> RepositoryDetailResponse | None:
        """
        Fetch repository, load constituent file reviews and findings, and return a full detail response.
        """
        result = await db.execute(
            select(Repository)
            .filter(Repository.id == repo_id)
            .options(
                selectinload(Repository.file_reviews)
                .selectinload(FileReview.review)
                .selectinload(Review.findings)
                .selectinload(Finding.ticket)
            )
        )
        repo = result.scalars().first()
        if not repo:
            return None

        # Build file response list
        files_list = []
        for fr in repo.file_reviews:
            review = fr.review
            findings_count = len(review.findings) if review and review.findings else 0
            tickets_count = sum(1 for f in review.findings if f.ticket) if review and review.findings else 0

            # Compute dynamic score
            from app.repositories.review_query_repository import compute_quality_score
            score = compute_quality_score(review.findings) if review and review.status == ReviewStatus.COMPLETED else 0

            files_list.append(
                FileReviewResponse(
                    id=fr.review_id,
                    file_path=fr.file_path,
                    language=review.language if review else "unknown",
                    status=review.status if review else "PENDING",
                    quality_score=score,
                    findings_count=findings_count,
                    tickets_count=tickets_count
                )
            )

        # Retrieve summary metrics
        metrics = repo.metrics or {}
        files_analyzed = metrics.get("files_analyzed", len(repo.file_reviews))
        critical_findings = metrics.get("critical_findings", 0)
        open_tickets = metrics.get("open_tickets", 0)
        largest_files = metrics.get("largest_files", [])
        most_problematic_files = metrics.get("most_problematic_files", [])

        # Calculate processing duration
        duration_seconds = None
        if repo.updated_at and repo.created_at:
            duration_seconds = (repo.updated_at - repo.created_at).total_seconds()

        return RepositoryDetailResponse(
            id=repo.id,
            name=repo.name,
            status=repo.status,
            created_at=repo.created_at,
            updated_at=repo.updated_at,
            language_summary=repo.language_summary or {},
            overall_quality=repo.overall_quality or 100,
            summary=repo.summary or "",
            files_analyzed=files_analyzed,
            critical_findings=critical_findings,
            open_tickets=open_tickets,
            duration_seconds=duration_seconds,
            files=files_list,
            largest_files=largest_files,
            most_problematic_files=most_problematic_files
        )

    async def list_repositories(
        self, db: AsyncSession, skip: int = 0, limit: int = 10
    ) -> tuple[list[Repository], int]:
        """
        List repositories with pagination.
        """
        total_result = await db.execute(select(func.count(Repository.id)))
        total = total_result.scalar_one() or 0

        result = await db.execute(
            select(Repository)
            .order_by(Repository.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def _run_repository_analysis_task(self, repo_id: int) -> None:
        """
        Execute parallel file analysis and aggregate repository-level metrics.
        """
        logger.info(f"Starting background repository analysis for ID {repo_id}")

        async with SessionLocal() as db:
            # 1. Transition Repository state to PROCESSING
            result = await db.execute(select(Repository).filter(Repository.id == repo_id))
            repo = result.scalars().first()
            if not repo:
                logger.error(f"Repository {repo_id} not found in background task.")
                return

            repo.status = ReviewStatus.PROCESSING
            await db.commit()

            # 2. Fetch all constituent FileReviews with reviews preloaded
            fr_result = await db.execute(
                select(FileReview)
                .filter(FileReview.repository_id == repo_id)
                .options(selectinload(FileReview.review))
            )
            file_reviews = list(fr_result.scalars().all())

            # 3. Generate and store embeddings for RAG retrieval
            from app.ai.router import get_ai_provider
            from app.ai.retrieval import repository_retrieval_service
            
            files_to_embed = [
                {"path": fr.file_path, "content": fr.review.code}
                for fr in file_reviews
                if fr.review and fr.review.code
            ]
            if files_to_embed:
                provider = get_ai_provider()
                await repository_retrieval_service.index_repository(db, repo_id, files_to_embed, provider)

        # 3. Process each FileReview concurrently (max 5 concurrent workers)
        sem = asyncio.Semaphore(5)

        async def analyze_single_file(fr_id: int, review_id: int):
            async with sem:
                async with SessionLocal() as task_db:
                    try:
                        # Re-run existing processing service on the Review id
                        await self.processing_svc.process_review(task_db, review_id)
                    except Exception as err:
                        logger.error(
                            f"Failed to analyze review {review_id} for file_review {fr_id}: {err}",
                            exc_info=True
                        )

        # Spawn all worker tasks
        tasks = [
            analyze_single_file(fr.id, fr.review_id)
            for fr in file_reviews
        ]
        await asyncio.gather(*tasks)

        # 4. Reload repository and compile summary stats
        async with SessionLocal() as db:
            result = await db.execute(
                select(Repository)
                .filter(Repository.id == repo_id)
                .options(
                    selectinload(Repository.file_reviews)
                    .selectinload(FileReview.review)
                    .selectinload(Review.findings)
                    .selectinload(Finding.ticket)
                )
            )
            repo = result.scalars().first()
            if not repo:
                return

            # Compute aggregations
            summary_data = RepositorySummary.aggregate(repo.file_reviews)

            # Update Repository record
            repo.status = ReviewStatus.COMPLETED
            repo.language_summary = summary_data["language_summary"]
            repo.overall_quality = summary_data["overall_quality"]
            repo.summary = summary_data["summary"]
            repo.metrics = summary_data["metrics"]
            repo.updated_at = datetime.now(UTC)

            await db.commit()
            logger.info(f"Completed background repository analysis for ID {repo_id}")


# Module-level singleton
repository_analysis_service = RepositoryAnalysisService()
