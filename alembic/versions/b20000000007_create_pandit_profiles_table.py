"""create pandit profiles table

Revision ID: b20000000007
Revises: b20000000006
Create Date: 2026-04-10 13:26:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000007"
down_revision = "b20000000006"
branch_labels = None
depends_on = None


pandit_status = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="pandit_profile_status",
    native_enum=False,
    create_constraint=True,
)


def upgrade():
    op.create_table(
        "pandit_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", pandit_status, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("avg_rating", sa.Float(), nullable=False),
        sa.Column("total_rating", sa.Integer(), nullable=False),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_pandit_profiles_id"), "pandit_profiles", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_pandit_profiles_id"), table_name="pandit_profiles")
    op.drop_table("pandit_profiles")
