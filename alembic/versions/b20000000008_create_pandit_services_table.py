"""create pandit services table

Revision ID: b20000000008
Revises: b20000000007
Create Date: 2026-04-10 13:27:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000008"
down_revision = "b20000000007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pandit_services",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("pandit_id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["pandit_id"], ["pandit_profiles.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pandit_id", "service_id", name="uq_pandit_service"),
    )
    op.create_index(op.f("ix_pandit_services_id"), "pandit_services", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_pandit_services_id"), table_name="pandit_services")
    op.drop_table("pandit_services")
