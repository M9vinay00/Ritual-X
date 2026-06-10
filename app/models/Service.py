"""Service reference model."""

import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Service(Base):
    """Represents a service that pandits can offer and users can book."""

    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    service_name = Column(String, nullable=False, unique=True)

    pandit_services = relationship("PanditService", back_populates="service")
    bookings = relationship("Booking", back_populates="service")
