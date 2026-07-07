"""add_enhanced_finding_fields

Revision ID: e61a990f85a2
Revises: 1a2b3c4d5e6f
Create Date: 2026-07-06 01:29:29.397494

Adds seven new nullable columns to the findings table to support the
enhanced AI Engineering Assistant review schema (EPIC-06 REVIEW-01).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e61a990f85a2"
down_revision: str | None = "1a2b3c4d5e6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add enhanced engineering metadata columns to findings (all nullable for backward compat)
    with op.batch_alter_table("findings", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("category", sa.String(length=50), nullable=True)
        )
        batch_op.add_column(
            sa.Column("confidence", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("impact", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("why_it_matters", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("improved_code", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("estimated_fix_time", sa.String(length=100), nullable=True)
        )
        batch_op.add_column(
            sa.Column("references", sa.JSON(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("findings", schema=None) as batch_op:
        batch_op.drop_column("references")
        batch_op.drop_column("estimated_fix_time")
        batch_op.drop_column("improved_code")
        batch_op.drop_column("why_it_matters")
        batch_op.drop_column("impact")
        batch_op.drop_column("confidence")
        batch_op.drop_column("category")
