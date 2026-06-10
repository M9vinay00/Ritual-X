"""create pandit languages table

Revision ID: b20000000009
Revises: b20000000008
Create Date: 2026-04-10 13:28:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000009"
down_revision = "b20000000008"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pandit_languages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("pandit_id", sa.UUID(), nullable=False),
        sa.Column("language_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
        sa.ForeignKeyConstraint(["pandit_id"], ["pandit_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pandit_id", "language_id", name="uq_pandit_language"),
    )
    op.create_index(op.f("ix_pandit_languages_id"), "pandit_languages", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_pandit_languages_id"), table_name="pandit_languages")
    op.drop_table("pandit_languages")
