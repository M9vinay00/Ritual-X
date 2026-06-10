"""add auth tables and super admin guard

Revision ID: b20000000016
Revises: b20000000015
Create Date: 2026-04-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000016"
down_revision = "b20000000015"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("is_super_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index(
        "uq_users_single_super_admin",
        "users",
        ["is_super_admin"],
        unique=True,
        postgresql_where=sa.text("is_super_admin = true"),
    )


def downgrade():
    op.drop_index("uq_users_single_super_admin", table_name="users")
    op.drop_column("users", "is_super_admin")
