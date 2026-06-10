"""create ratings table

Revision ID: b20000000013
Revises: b20000000012
Create Date: 2026-04-10 13:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000013"
down_revision = "b20000000012"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ratings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("pandit_id", sa.UUID(), nullable=False),
        sa.Column("booking_id", sa.UUID(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review", sa.String(), nullable=True),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_ratings_rating_range"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["pandit_id"], ["pandit_profiles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index(op.f("ix_ratings_id"), "ratings", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_ratings_id"), table_name="ratings")
    op.drop_table("ratings")
