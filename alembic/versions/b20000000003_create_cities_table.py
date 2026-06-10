"""create cities table

Revision ID: b20000000003
Revises: b20000000002
Create Date: 2026-04-10 13:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000003"
down_revision = "b20000000002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("state_id", sa.UUID(), nullable=False),
        sa.Column("city_name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["state_id"], ["states.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_id", "city_name", name="uq_city_state_name"),
    )
    op.create_index(op.f("ix_cities_id"), "cities", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_cities_id"), table_name="cities")
    op.drop_table("cities")
