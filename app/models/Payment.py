"""Payment model for booking transactions."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import PaymentMethod, PaymentStatus, db_enum


class Payment(Base):
    """Tracks payment details for a booking."""

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, unique=True)
    amount = Column(Float, nullable=False, default=0, comment="Actual paid amount")
    payment_method = Column(db_enum(PaymentMethod, "payment_method"), nullable=False)
    payment_status = Column(
        db_enum(PaymentStatus, "payment_status"),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    transaction_id = Column(String, nullable=True)

    booking = relationship("Booking", back_populates="payment")
