"""fix booking status constraint

Revision ID: b20000000020
Revises: b20000000019
Create Date: 2026-04-17 15:05:00.000000

"""

from alembic import op


revision = "b20000000020"
down_revision = "b20000000019"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS booking_status")
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT booking_status
        CHECK (status IN ('pending', 'confirmed', 'rejected', 'completed', 'cancelled'))
        """
    )


def downgrade():
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS booking_status")
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT booking_status
        CHECK (status IN ('pending', 'confirmed', 'rejected', 'completed'))
        """
    )
