"""User account model."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .mixins import TimestampMixin, UserAuditMixin


class User(TimestampMixin, UserAuditMixin, Base):
    """Represents a platform account for admins, users, and pandits."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=True)
    preferred_language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_super_admin = Column(Boolean, nullable=False, default=False)
    forgot_password_token = Column(String, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)

    role = relationship("Role", back_populates="users")
    city = relationship("City", back_populates="users")
    preferred_language = relationship("Language", back_populates="preferred_by_users")
    created_by_user = relationship("User", foreign_keys="User.created_by", remote_side=[id])
    updated_by_user = relationship("User", foreign_keys="User.updated_by", remote_side=[id])
    pandit_profile = relationship(
        "PanditProfile",
        foreign_keys="PanditProfile.user_id",
        back_populates="user",
        uselist=False,
    )
    user_bookings = relationship("Booking", foreign_keys="Booking.user_id", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    created_pandit_profiles = relationship("PanditProfile", foreign_keys="PanditProfile.created_by")
    updated_pandit_profiles = relationship("PanditProfile", foreign_keys="PanditProfile.updated_by")
