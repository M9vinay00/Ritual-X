"""Pandit profile model."""

import uuid

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import PanditProfileStatus, db_enum
from .mixins import TimestampMixin, UserAuditMixin


class PanditProfile(TimestampMixin, UserAuditMixin, Base):
    """Extends a user account with pandit-specific business data."""

    __tablename__ = "pandit_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    experience_years = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    status = Column(
        db_enum(PanditProfileStatus, "pandit_profile_status"),
        nullable=False,
        default=PanditProfileStatus.PENDING,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    avg_rating = Column(Float, nullable=False, default=0)
    total_rating = Column(Integer, nullable=False, default=0)
    rating_count = Column(Integer, nullable=False, default=0)

    user = relationship("User", foreign_keys=[user_id], back_populates="pandit_profile")
    created_by_user = relationship(
        "User",
        foreign_keys="PanditProfile.created_by",
        back_populates="created_pandit_profiles",
    )
    updated_by_user = relationship(
        "User",
        foreign_keys="PanditProfile.updated_by",
        back_populates="updated_pandit_profiles",
    )
    services = relationship("PanditService", back_populates="pandit_profile")
    languages = relationship("PanditLanguage", back_populates="pandit_profile")
    availability_slots = relationship("AvailabilitySlot", back_populates="pandit_profile")
    bookings = relationship("Booking", back_populates="pandit_profile")
    ratings = relationship("Rating", back_populates="pandit_profile")
