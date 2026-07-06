from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import TicketPriority, TicketStatus

if TYPE_CHECKING:
    from app.models.finding import Finding


class Ticket(Base):
    """SQLAlchemy model representing a trackable bug ticket generated from an AI finding."""

    __tablename__ = "tickets"

    finding_id: Mapped[int] = mapped_column(
        sa.ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Ensures 1-to-1 relationship limit
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[TicketPriority] = mapped_column(
        sa.Enum(TicketPriority),
        default=TicketPriority.P2,
        nullable=False,
    )
    status: Mapped[TicketStatus] = mapped_column(
        sa.Enum(TicketStatus),
        default=TicketStatus.OPEN,
        nullable=False,
    )
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    finding: Mapped[Finding] = relationship("Finding", back_populates="ticket")
