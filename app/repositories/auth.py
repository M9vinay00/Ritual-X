"""Database access helpers used by authentication workflows."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import func

from app.models import City, Language, PanditProfile, Role, User


class AuthRepository:
    """Encapsulate user, role, city, and language queries for auth flows."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Return a role by its canonical name."""
        result = await self.db.execute(select(Role).where(Role.role_name == role_name))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Return a user by email with auth-related relationships loaded."""
        statement = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.pandit_profile),
                selectinload(User.city),
                selectinload(User.preferred_language),
            )
            .where(User.email == email)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """Return a user by phone number when present."""
        statement = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.pandit_profile),
            )
            .where(User.phone == phone)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_reset_token(self, email: str, token_hash: str) -> Optional[User]:
        """Return the user owning a specific hashed reset token."""
        statement = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.pandit_profile),
                selectinload(User.city),
                selectinload(User.preferred_language),
            )
            .where(User.email == email, User.forgot_password_token == token_hash)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Return a user by primary key with common relationships loaded."""
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

    async def get_city_by_name(self, city_name: str) -> Optional[City]:
        """Return a city by normalized name."""
        result = await self.db.execute(
            select(City)
            .options(selectinload(City.state))
            .where(func.lower(City.city_name) == city_name.strip().lower())
        )
        return result.scalar_one_or_none()

    async def get_language_by_name(self, language_name: str) -> Optional[Language]:
        """Return a language by normalized name."""
        result = await self.db.execute(
            select(Language).where(func.lower(Language.language_name) == language_name.strip().lower())
        )
        return result.scalar_one_or_none()

    async def super_admin_exists(self) -> bool:
        """Check whether the platform already has a super admin account."""
        result = await self.db.execute(select(User.id).where(User.is_super_admin.is_(True)))
        return result.scalar_one_or_none() is not None

    async def create_user(self, **kwargs) -> User:
        """Stage a new user for insertion and return the ORM object."""
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()
        return user

    async def create_pandit_profile(self, **kwargs) -> PanditProfile:
        """Stage a new pandit profile for insertion and return the ORM object."""
        profile = PanditProfile(**kwargs)
        self.db.add(profile)
        await self.db.flush()
        return profile
