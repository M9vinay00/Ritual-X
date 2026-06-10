"""create admin revenues table

Revision ID: b20000000014
Revises: b20000000013
Create Date: 2026-04-10 13:33:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000014"
down_revision = "b20000000013"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_revenues",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("booking_id", sa.UUID(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("admin_share", sa.Float(), nullable=False),
        sa.Column("pandit_share", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index(op.f("ix_admin_revenues_id"), "admin_revenues", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_admin_revenues_id"), table_name="admin_revenues")
    op.drop_table("admin_revenues")
