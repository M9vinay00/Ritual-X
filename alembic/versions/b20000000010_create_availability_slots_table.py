"""create availability slots table

Revision ID: b20000000010
Revises: b20000000009
Create Date: 2026-04-10 13:29:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000010"
down_revision = "b20000000009"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "availability_slots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("pandit_id", sa.UUID(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_booked", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["pandit_id"], ["pandit_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pandit_id", "start_time", "end_time", name="uq_pandit_slot_time"),
    )
    op.create_index(op.f("ix_availability_slots_id"), "availability_slots", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_availability_slots_id"), table_name="availability_slots")
    op.drop_table("availability_slots")
