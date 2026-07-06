from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import FindingCategory, FindingStatus

if TYPE_CHECKING:
    from app.models.review import Review
    from app.models.ticket import Ticket


class Finding(Base):
    """SQLAlchemy model representing an individual issue identified in a review."""

    __tablename__ = "findings"

    review_id: Mapped[int] = mapped_column(sa.ForeignKey("reviews.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[FindingStatus] = mapped_column(
        sa.Enum(FindingStatus), default=FindingStatus.OPEN, nullable=False
    )
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_case_hint: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Enhanced engineering metadata fields (nullable for backward compatibility)
    category: Mapped[str | None] = mapped_column(
        sa.Enum(FindingCategory), default=FindingCategory.UNKNOWN, nullable=True
    )
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    why_it_matters: Mapped[str | None] = mapped_column(Text, nullable=True)
    improved_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_fix_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    references: Mapped[list | None] = mapped_column(sa.JSON, nullable=True)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    review: Mapped[Review] = relationship("Review", back_populates="findings")
    ticket: Mapped[Ticket | None] = relationship(
        "Ticket",
        back_populates="finding",
        cascade="all, delete-orphan",
        uselist=False,
    )

