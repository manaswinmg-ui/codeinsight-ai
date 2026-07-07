from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self) -> None:
        super().__init__(Review)

    async def create_review(
        self,
        db: AsyncSession,
        *,
        code: str,
        language: str,
        summary: str,
        raw_response: dict,
        user_id: int | None = None,
    ) -> Review:
        """Persist a new review record."""
        db_obj = Review(
            code=code,
            language=language,
            summary=summary,
            raw_response=raw_response,
            status="completed",
            user_id=user_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


review_repository = ReviewRepository()
