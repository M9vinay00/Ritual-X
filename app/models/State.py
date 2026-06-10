"""State reference model."""

import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class State(Base):
    """Represents a state and its default language."""

    __tablename__ = "states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    state_name = Column(String, nullable=False, unique=True)
    default_language = Column(String, nullable=False)

    cities = relationship("City", back_populates="state")
