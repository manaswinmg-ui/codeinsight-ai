from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RepositoryEmbedding(Base):
    """Stores tokenized text chunks and their embeddings for similarity searches."""

    __tablename__ = "repository_embeddings"

    repository_id: Mapped[int] = mapped_column(
        sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(sa.String(1024), nullable=False)
    chunk_index: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(sa.JSON, nullable=False)
