"""create bookings table

Revision ID: b20000000011
Revises: b20000000010
Create Date: 2026-04-10 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000011"
down_revision = "b20000000010"
branch_labels = None
depends_on = None


booking_status = sa.Enum(
    "pending",
    "confirmed",
    "rejected",
    "completed",
    name="booking_status",
    native_enum=False,
    create_constraint=True,
)
booking_payment_status = sa.Enum(
    "pending",
    "paid",
    "completed",
    "failed",
    name="booking_payment_status",
    native_enum=False,
    create_constraint=True,
)


def upgrade():
    op.create_table(
        "bookings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("pandit_id", sa.UUID(), nullable=False),
        sa.Column("slot_id", sa.UUID(), nullable=True),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", booking_status, nullable=False),
        sa.Column("amount", sa.Float(), nullable=False, comment="Expected booking amount"),
        sa.Column("payment_status", booking_payment_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["pandit_id"], ["pandit_profiles.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.ForeignKeyConstraint(["slot_id"], ["availability_slots.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slot_id"),
    )
    op.create_index(op.f("ix_bookings_id"), "bookings", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_bookings_id"), table_name="bookings")
    op.drop_table("bookings")
