import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.response_parser import ReviewResult
from app.ai.review_pipeline import AIReviewPipeline
from app.mappers.finding_mapper import FindingMapper
from app.models.enums import ReviewStatus
from app.repositories.finding_repository import FindingRepository, finding_repository
from app.repositories.review_query_repository import compute_quality_score
from app.repositories.review_repository import ReviewRepository, review_repository

logger = logging.getLogger("app.services.review_processing")


class ReviewProcessingService:
    def __init__(
        self,
        repository: ReviewRepository = review_repository,
        ai_pipeline: AIReviewPipeline = AIReviewPipeline(),
        finding_mapper: FindingMapper = FindingMapper(),
        finding_repository: FindingRepository = finding_repository,
    ) -> None:
        self.repository = repository
        self.ai_pipeline = ai_pipeline
        self.finding_mapper = finding_mapper
        self.finding_repository = finding_repository

    async def process_review(self, db: AsyncSession, review_id: int) -> ReviewResult:
        """Retrieve review, update status, run AI review, and persist findings."""
        review = await self.repository.get_by_id(db, review_id)
        if not review:
            raise ValueError(f"Review with id {review_id} not found")

        # Transition PENDING -> PROCESSING
        review.status = ReviewStatus.PROCESSING
        review = await self.repository.update(db, review=review)
        logger.info(f"Review {review_id} transitioned to PROCESSING state.")

        try:
            # Step 1: Run AI analysis facade pipeline
            review_result = await self.ai_pipeline.process(review)

            # Step 2: Map findings to transient ORM models
            finding_entities = self.finding_mapper.map(review, review_result)

            # Step 3: Persist findings in a single transaction
            await self.finding_repository.create_many(db, findings=finding_entities)
            logger.info(
                f"Persisted {len(finding_entities)} findings for Review {review_id}."
            )

            # Transition PROCESSING -> COMPLETED
            review.status = ReviewStatus.COMPLETED
            review.quality_score = compute_quality_score(finding_entities)
            await self.repository.update(db, review=review)
            logger.info(f"Review {review_id} completed successfully.")

            return review_result

        except Exception as err:
            logger.error(
                f"Exception encountered during review processing for ID {review_id}: "
                f"{str(err)}",
                exc_info=True,
            )
            # Transition to FAILED state
            review.status = ReviewStatus.FAILED
            await self.repository.update(db, review=review)
            raise err


review_processing_service = ReviewProcessingService()
