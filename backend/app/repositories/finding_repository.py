from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.finding import Finding
from app.repositories.base import BaseRepository


class FindingRepository(BaseRepository[Finding]):
    def __init__(self) -> None:
        super().__init__(Finding)

    async def get_with_review(
        self, db: AsyncSession, finding_id: int
    ) -> Finding | None:
        """Retrieve a Finding by its ID eagerly loading its associated Review."""
        result = await db.execute(
            select(Finding)
            .filter(Finding.id == finding_id)
            .options(selectinload(Finding.review))
        )
        return result.scalars().first()

    async def create_many(
        self, db: AsyncSession, *, findings: list[Finding]
    ) -> list[Finding]:
        """Persist multiple Finding entities in a single transaction."""
        db.add_all(findings)
        await db.commit()
        for f in findings:
            await db.refresh(f)
        return findings


finding_repository = FindingRepository()
