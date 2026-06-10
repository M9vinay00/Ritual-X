"""Join model between pandits and the services they offer."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class PanditService(Base):
    """Stores one service offering and price for a pandit."""

    __tablename__ = "pandit_services"
    __table_args__ = (UniqueConstraint("pandit_id", "service_id", name="uq_pandit_service"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    pandit_id = Column(UUID(as_uuid=True), ForeignKey("pandit_profiles.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    price = Column(Float, nullable=False, default=0)

    pandit_profile = relationship("PanditProfile", back_populates="services")
    service = relationship("Service", back_populates="pandit_services")
