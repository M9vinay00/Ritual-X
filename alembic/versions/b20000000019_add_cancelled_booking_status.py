"""add cancelled booking status

Revision ID: b20000000019
Revises: b20000000018
Create Date: 2026-04-17 14:55:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "b20000000019"
down_revision = "b20000000018"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("booking_status", "bookings", type_="check")
    op.create_check_constraint(
        "booking_status",
        "bookings",
        sa.text("status IN ('pending', 'confirmed', 'rejected', 'completed', 'cancelled')"),
    )


def downgrade():
    op.drop_constraint("booking_status", "bookings", type_="check")
    op.create_check_constraint(
        "booking_status",
        "bookings",
        sa.text("status IN ('pending', 'confirmed', 'rejected', 'completed')"),
    )
