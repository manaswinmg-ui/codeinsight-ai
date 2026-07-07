from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self) -> None:
        super().__init__(Review)

    async def create(self, db: AsyncSession, *, review: Review) -> Review:
        """Persist a new Review record."""
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

    async def get_by_id(self, db: AsyncSession, review_id: int) -> Review | None:
        """Retrieve a Review by its integer ID."""
        result = await db.execute(select(Review).filter(Review.id == review_id))
        return result.scalars().first()

    async def get_with_findings(self, db: AsyncSession, review_id: int) -> Review | None:
        """Retrieve a Review by ID, eagerly loading its findings relationship."""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Review)
            .filter(Review.id == review_id)
            .options(selectinload(Review.findings))
        )
        return result.scalars().first()

    async def update(self, db: AsyncSession, *, review: Review) -> Review:
        """Persist updates to an existing Review."""
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

    async def delete(self, db: AsyncSession, review_id: int) -> bool:
        """Delete a Review record by ID. Returns True if deleted, False if not found."""
        review = await self.get_by_id(db, review_id)
        if not review:
            return False
        await db.delete(review)
        await db.commit()
        return True


review_repository = ReviewRepository()
