"""create states table

Revision ID: b20000000002
Revises: b20000000001
Create Date: 2026-04-10 13:21:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000002"
down_revision = "b20000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "states",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("state_name", sa.String(), nullable=False),
        sa.Column("default_language", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_name"),
    )
    op.create_index(op.f("ix_states_id"), "states", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_states_id"), table_name="states")
    op.drop_table("states")
