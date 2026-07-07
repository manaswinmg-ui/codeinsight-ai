from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.review import Review
    from app.models.ticket import Ticket


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    reviews: Mapped[list[Review]] = relationship(
        "Review", back_populates="owner", lazy="selectin"
    )
    tickets: Mapped[list[Ticket]] = relationship(
        "Ticket", back_populates="owner", lazy="selectin"
    )
    repositories: Mapped[list[Repository]] = relationship(
        "Repository", back_populates="owner", lazy="selectin"
    )
