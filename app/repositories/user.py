"""Database queries used by user self-service flows."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import City, Language, User


class UserRepository:
    """Encapsulate common user, city, and language lookups."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Return a user by id with relationships needed by the API."""
        statement = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.pandit_profile),
                selectinload(User.city),
                selectinload(User.preferred_language),
            )
            .where(User.id == user_id)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_city_by_id(self, city_id: UUID) -> Optional[City]:
        """Return a city by primary key."""
        result = await self.db.execute(select(City).where(City.id == city_id))
        return result.scalar_one_or_none()

    async def get_language_by_id(self, language_id: UUID) -> Optional[Language]:
        """Return a language by primary key."""
        result = await self.db.execute(select(Language).where(Language.id == language_id))
        return result.scalar_one_or_none()

    async def get_city_by_name(self, city_name: str) -> Optional[City]:
        """Return a city by normalized name."""
        result = await self.db.execute(select(City).where(func.lower(City.city_name) == city_name.strip().lower()))
        return result.scalar_one_or_none()

    async def get_language_by_name(self, language_name: str) -> Optional[Language]:
        """Return a language by normalized name."""
        result = await self.db.execute(
            select(Language).where(func.lower(Language.language_name) == language_name.strip().lower())
        )
        return result.scalar_one_or_none()
