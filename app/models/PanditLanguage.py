"""Join model between pandit profiles and languages."""

import uuid

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class PanditLanguage(Base):
    """Stores which languages a pandit can communicate in."""

    __tablename__ = "pandit_languages"
    __table_args__ = (UniqueConstraint("pandit_id", "language_id", name="uq_pandit_language"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    pandit_id = Column(UUID(as_uuid=True), ForeignKey("pandit_profiles.id"), nullable=False)
    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False)

    pandit_profile = relationship("PanditProfile", back_populates="languages")
    language = relationship("Language", back_populates="pandit_languages")
