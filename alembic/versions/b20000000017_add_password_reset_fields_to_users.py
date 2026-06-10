"""add password reset fields to users

Revision ID: b20000000017
Revises: b20000000016
Create Date: 2026-04-13 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b20000000017"
down_revision = "b20000000016"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("forgot_password_token", sa.String(), nullable=True))
    op.add_column("users", sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("users", "token_expiry")
    op.drop_column("users", "forgot_password_token")
