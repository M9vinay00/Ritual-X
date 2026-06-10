"""Role reference model."""

import uuid

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Role(Base):
    """Represents an application role such as admin, user, or pandit."""

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("role_name", name="uq_roles_role_name"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    role_name = Column(String, nullable=False)

    users = relationship("User", back_populates="role")
