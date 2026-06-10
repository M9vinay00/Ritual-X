"""Pandit availability slot model."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class AvailabilitySlot(Base):
    """Represents a bookable time window published by a pandit."""

    __tablename__ = "availability_slots"
    __table_args__ = (UniqueConstraint("pandit_id", "start_time", "end_time", name="uq_pandit_slot_time"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    pandit_id = Column(UUID(as_uuid=True), ForeignKey("pandit_profiles.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_booked = Column(Boolean, nullable=False, default=False)

    pandit_profile = relationship("PanditProfile", back_populates="availability_slots")
    booking = relationship("Booking", back_populates="slot", uselist=False)
