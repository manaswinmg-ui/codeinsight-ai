"""add_user_auth_fields

Revision ID: 6735577a0f5c
Revises: 98e463d591e2
Create Date: 2026-07-08 00:57:45.652209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6735577a0f5c'
down_revision: Union[str, None] = '98e463d591e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add username to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=150), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)
    
    # 2. Add user_id to reviews, tickets, and repositories tables using batch_op for SQLite compatibility
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_reviews_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_reviews_user_id_users', 'users', ['user_id'], ['id'], ondelete='SET NULL')

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_tickets_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_tickets_user_id_users', 'users', ['user_id'], ['id'], ondelete='SET NULL')

    with op.batch_alter_table('repositories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_repositories_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_repositories_user_id_users', 'users', ['user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    with op.batch_alter_table('repositories', schema=None) as batch_op:
        batch_op.drop_constraint('fk_repositories_user_id_users', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_repositories_user_id'))
        batch_op.drop_column('user_id')

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.drop_constraint('fk_tickets_user_id_users', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_tickets_user_id'))
        batch_op.drop_column('user_id')

    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_constraint('fk_reviews_user_id_users', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_reviews_user_id'))
        batch_op.drop_column('user_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_column('username')
