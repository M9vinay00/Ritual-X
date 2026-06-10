"""create payments table

Revision ID: b20000000012
Revises: b20000000011
Create Date: 2026-04-10 13:31:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000012"
down_revision = "b20000000011"
branch_labels = None
depends_on = None


payment_method = sa.Enum(
    "cash",
    "upi",
    "online",
    name="payment_method",
    native_enum=False,
    create_constraint=True,
)
payment_status = sa.Enum(
    "pending",
    "paid",
    "completed",
    "failed",
    name="payment_status",
    native_enum=False,
    create_constraint=True,
)


def upgrade():
    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("booking_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False, comment="Actual paid amount"),
        sa.Column("payment_method", payment_method, nullable=False),
        sa.Column("payment_status", payment_status, nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_table("payments")
