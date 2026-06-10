"""update roles table

Revision ID: b20000000001
Revises: df60dc6a87b6
Create Date: 2026-04-10 13:20:00.000000

"""
from alembic import op


revision = "b20000000001"
down_revision = "df60dc6a87b6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("roles", "role", new_column_name="role_name")
    op.create_unique_constraint("uq_roles_role_name", "roles", ["role_name"])


def downgrade():
    op.drop_constraint("uq_roles_role_name", "roles", type_="unique")
    op.alter_column("roles", "role_name", new_column_name="role")
