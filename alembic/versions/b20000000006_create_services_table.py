"""create services table

Revision ID: b20000000006
Revises: b20000000005
Create Date: 2026-04-10 13:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000006"
down_revision = "b20000000005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "services",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("service_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_name"),
    )
    op.create_index(op.f("ix_services_id"), "services", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_services_id"), table_name="services")
    op.drop_table("services")
