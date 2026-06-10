"""create languages table

Revision ID: b20000000004
Revises: b20000000003
Create Date: 2026-04-10 13:23:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000004"
down_revision = "b20000000003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "languages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("language_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("language_name"),
    )
    op.create_index(op.f("ix_languages_id"), "languages", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_languages_id"), table_name="languages")
    op.drop_table("languages")
