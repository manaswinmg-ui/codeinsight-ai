from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ReviewStatus

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.user import User


class Review(Base):
    """SQLAlchemy model representing a code review request."""

    __tablename__ = "reviews"

    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(
        sa.Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False
    )

    # Owner (nullable for backward compatibility with pre-auth data)
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    quality_score: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    # Relationships
    findings: Mapped[list[Finding]] = relationship(
        "Finding",
        back_populates="review",
        cascade="all, delete-orphan",
    )
    owner: Mapped[User | None] = relationship("User", back_populates="reviews")
