"""add rejection reason to pandit profiles

Revision ID: b20000000018
Revises: b20000000017
Create Date: 2026-04-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b20000000018"
down_revision = "b20000000017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pandit_profiles", sa.Column("rejection_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("pandit_profiles", "rejection_reason")
