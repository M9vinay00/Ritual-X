"""Admin revenue split model."""

import uuid

from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class AdminRevenue(Base):
    """Stores how each completed booking amount is split."""

    __tablename__ = "admin_revenues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, unique=True)
    total_amount = Column(Float, nullable=False, default=0)
    admin_share = Column(Float, nullable=False, default=0)
    pandit_share = Column(Float, nullable=False, default=0)

    booking = relationship("Booking", back_populates="admin_revenue")
