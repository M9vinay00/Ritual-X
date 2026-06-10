"""add created by audit columns

Revision ID: b20000000015
Revises: b20000000014
Create Date: 2026-04-10 16:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000015"
down_revision = "b20000000014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_users_created_by_users", "users", "users", ["created_by"], ["id"])

    op.add_column("pandit_profiles", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_pandit_profiles_created_by_users",
        "pandit_profiles",
        "users",
        ["created_by"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_pandit_profiles_created_by_users", "pandit_profiles", type_="foreignkey")
    op.drop_column("pandit_profiles", "created_by")

    op.drop_constraint("fk_users_created_by_users", "users", type_="foreignkey")
    op.drop_column("users", "created_by")
