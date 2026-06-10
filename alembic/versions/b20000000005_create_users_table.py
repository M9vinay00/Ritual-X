"""create users table

Revision ID: b20000000005
Revises: b20000000004
Create Date: 2026-04-10 13:24:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000005"
down_revision = "b20000000004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("city_id", sa.UUID(), nullable=True),
        sa.Column("preferred_language_id", sa.UUID(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"]),
        sa.ForeignKeyConstraint(["preferred_language_id"], ["languages.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
