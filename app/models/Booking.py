"""Booking model linking users, pandits, services, and payments."""

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import BookingStatus, PaymentStatus, db_enum
from .mixins import TimestampMixin


class Booking(TimestampMixin, Base):
    """Represents one booking request or confirmed appointment."""

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pandit_id = Column(UUID(as_uuid=True), ForeignKey("pandit_profiles.id"), nullable=False)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("availability_slots.id"), nullable=True, unique=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(db_enum(BookingStatus, "booking_status"), nullable=False, default=BookingStatus.PENDING)
    amount = Column(Float, nullable=False, default=0, comment="Expected booking amount")
    payment_status = Column(
        db_enum(PaymentStatus, "booking_payment_status"),
        nullable=False,
        default=PaymentStatus.PENDING,
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="user_bookings")
    pandit_profile = relationship("PanditProfile", back_populates="bookings")
    slot = relationship("AvailabilitySlot", back_populates="booking")
    service = relationship("Service", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    rating = relationship("Rating", back_populates="booking", uselist=False)
    admin_revenue = relationship("AdminRevenue", back_populates="booking", uselist=False)
