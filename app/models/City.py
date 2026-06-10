"""City reference model."""

import uuid

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class City(Base):
    """Represents a city within a seeded state."""

    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("state_id", "city_name", name="uq_city_state_name"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=False)
    city_name = Column(String, nullable=False)

    state = relationship("State", back_populates="cities")
    users = relationship("User", back_populates="city")
