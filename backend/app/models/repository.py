from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ReviewStatus
from app.models.review import Review

if TYPE_CHECKING:
    from app.models.user import User


class Repository(Base):
    """SQLAlchemy model representing a multi-file repository review request."""

    __tablename__ = "repositories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(
        sa.Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False
    )
    language_summary: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    overall_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    
    root_path: Mapped[str | None] = mapped_column(sa.String(1024), nullable=True)
    total_files: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)
    supported_files: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)
    ignored_files: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)
    scan_duration: Mapped[float | None] = mapped_column(sa.Float, nullable=True)

    # Owner (nullable for backward compatibility with pre-auth data)
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    file_reviews: Mapped[list[FileReview]] = relationship(
        "FileReview",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    owner: Mapped[User | None] = relationship("User", back_populates="repositories")


class FileReview(Base):
    """Mapping table linking a Repository to its constituent source file Reviews."""

    __tablename__ = "file_reviews"

    repository_id: Mapped[int] = mapped_column(
        sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    review_id: Mapped[int] = mapped_column(
        sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    repository: Mapped[Repository] = relationship("Repository", back_populates="file_reviews")
    review: Mapped[Review] = relationship("Review")
