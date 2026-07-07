from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ReviewStatus
from app.models.review import Review
from app.repositories.review_repository import ReviewRepository, review_repository


class ReviewService:
    def __init__(self, repository: ReviewRepository = review_repository) -> None:
        self.repository = repository

    async def create_review(
        self, db: AsyncSession, *, code: str, language: str, user_id: int | None = None
    ) -> Review:
        """Validate and create a new review record with status PENDING."""
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")
        if not language or not language.strip():
            raise ValueError("Language cannot be empty")

        review = Review(
            code=code.strip(),
            language=language.strip(),
            status=ReviewStatus.PENDING,
            user_id=user_id,
        )

        return await self.repository.create(db, review=review)

    async def get_review(self, db: AsyncSession, review_id: int) -> Review | None:
        """Retrieve a review by ID."""
        return await self.repository.get_by_id(db, review_id)

    async def get_review_with_findings(
        self, db: AsyncSession, review_id: int
    ) -> Review | None:
        """Retrieve review with eagerly loaded findings."""
        return await self.repository.get_with_findings(db, review_id)

    async def delete_review(self, db: AsyncSession, review_id: int) -> bool:
        """Delete a review by ID."""
        return await self.repository.delete(db, review_id)


review_service = ReviewService()
