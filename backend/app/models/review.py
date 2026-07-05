from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ReviewStatus

if TYPE_CHECKING:
    from app.models.finding import Finding


class Review(Base):
    """SQLAlchemy model representing a code review request."""

    __tablename__ = "reviews"

    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(
        sa.Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False
    )

    # Relationships
    findings: Mapped[list[Finding]] = relationship(
        "Finding",
        back_populates="review",
        cascade="all, delete-orphan",
    )
