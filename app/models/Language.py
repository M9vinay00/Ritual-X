"""Language reference model."""

import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Language(Base):
    """Represents a supported language on the platform."""

    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    language_name = Column(String, nullable=False, unique=True)

    preferred_by_users = relationship("User", back_populates="preferred_language")
    pandit_languages = relationship("PanditLanguage", back_populates="language")
