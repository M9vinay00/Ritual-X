"""Reusable SQLAlchemy mixins for timestamps and audit fields."""

from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID


class TimestampMixin:
    """Adds created/updated timestamp columns to a model."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UserAuditMixin:
    """Adds created_by and updated_by user references to a model."""

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
