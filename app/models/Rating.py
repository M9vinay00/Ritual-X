"""Rating and review model for completed bookings."""

import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Rating(Base):
    """Stores one user's rating for one completed booking."""

    __tablename__ = "ratings"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_ratings_rating_range"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pandit_id = Column(UUID(as_uuid=True), ForeignKey("pandit_profiles.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)
    review = Column(String, nullable=True)

    user = relationship("User", back_populates="ratings")
    pandit_profile = relationship("PanditProfile", back_populates="ratings")
    booking = relationship("Booking", back_populates="rating")
