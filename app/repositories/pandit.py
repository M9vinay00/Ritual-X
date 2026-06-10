"""Database queries that support pandit-facing workflows."""

from typing import Optional
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    AdminRevenue,
    AvailabilitySlot,
    Booking,
    City,
    Language,
    PanditLanguage,
    PanditProfile,
    PanditService,
    Rating,
    Service,
    User,
)
from app.models.enums import BookingStatus, PanditProfileStatus


class PanditRepository:
    """Encapsulate pandit profile, service, slot, and earnings queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_pandits(
        self,
        *,
        city_name: str | None = None,
        service_name: str | None = None,
        language_name: str | None = None,
    ) -> list[PanditProfile]:
        """Search approved, active pandits using optional discovery filters."""
        statement = (
            select(PanditProfile)
            .join(User, PanditProfile.user_id == User.id)
            .options(
                selectinload(PanditProfile.user).selectinload(User.role),
                selectinload(PanditProfile.user).selectinload(User.city),
                selectinload(PanditProfile.services).selectinload(PanditService.service),
                selectinload(PanditProfile.languages).selectinload(PanditLanguage.language),
            )
            .where(
                PanditProfile.status == PanditProfileStatus.APPROVED,
                PanditProfile.is_active.is_(True),
                User.is_active.is_(True),
            )
        )

        if city_name:
            statement = statement.join(City, User.city_id == City.id).where(City.city_name.ilike(f"%{city_name}%"))
        if service_name:
            statement = (
                statement.join(PanditService, PanditService.pandit_id == PanditProfile.id)
                .join(Service, PanditService.service_id == Service.id)
                .where(Service.service_name.ilike(f"%{service_name}%"))
            )
        if language_name:
            statement = (
                statement.join(PanditLanguage, PanditLanguage.pandit_id == PanditProfile.id)
                .join(Language, PanditLanguage.language_id == Language.id)
                .where(Language.language_name.ilike(f"%{language_name}%"))
            )

        result = await self.db.execute(statement.distinct())
        return result.scalars().all()

    async def get_public_pandit_by_id(self, pandit_id: UUID) -> Optional[PanditProfile]:
        """Return one approved pandit profile for public display."""
        statement = (
            select(PanditProfile)
            .join(User, PanditProfile.user_id == User.id)
            .options(
                selectinload(PanditProfile.user).selectinload(User.role),
                selectinload(PanditProfile.user).selectinload(User.city),
                selectinload(PanditProfile.services).selectinload(PanditService.service),
                selectinload(PanditProfile.languages).selectinload(PanditLanguage.language),
                selectinload(PanditProfile.ratings).selectinload(Rating.user),
            )
            .where(
                PanditProfile.id == pandit_id,
                PanditProfile.status == PanditProfileStatus.APPROVED,
                PanditProfile.is_active.is_(True),
                User.is_active.is_(True),
            )
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_pandit_profile_by_user_id(self, user_id: UUID) -> Optional[PanditProfile]:
        """Return the pandit profile linked to a user account."""
        statement = (
            select(PanditProfile)
            .options(
                selectinload(PanditProfile.user).selectinload(User.role),
                selectinload(PanditProfile.user).selectinload(User.city),
                selectinload(PanditProfile.services).selectinload(PanditService.service),
                selectinload(PanditProfile.languages).selectinload(PanditLanguage.language),
                selectinload(PanditProfile.ratings).selectinload(Rating.user),
            )
            .where(PanditProfile.user_id == user_id)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_service_by_name(self, service_name: str) -> Optional[Service]:
        """Return a service by normalized name."""
        result = await self.db.execute(
            select(Service).where(func.lower(Service.service_name) == service_name.strip().lower())
        )
        return result.scalar_one_or_none()

    async def get_city_by_name(self, city_name: str) -> Optional[City]:
        """Return a city by normalized name."""
        result = await self.db.execute(select(City).where(func.lower(City.city_name) == city_name.strip().lower()))
        return result.scalar_one_or_none()

    async def get_languages_by_names(self, language_names: list[str]) -> list[Language]:
        """Return all languages matching the provided normalized names."""
        if not language_names:
            return []

        normalized_names = [language_name.strip().lower() for language_name in language_names]
        result = await self.db.execute(select(Language).where(func.lower(Language.language_name).in_(normalized_names)))
        return result.scalars().all()

    async def get_pandit_service(self, pandit_id: UUID, service_id: UUID) -> Optional[PanditService]:
        """Return one pandit-service mapping by ids."""
        result = await self.db.execute(
            select(PanditService).where(PanditService.pandit_id == pandit_id, PanditService.service_id == service_id)
        )
        return result.scalar_one_or_none()

    async def get_pandit_service_by_name(self, pandit_id: UUID, service_name: str) -> Optional[PanditService]:
        """Return one pandit-service mapping by service name."""
        result = await self.db.execute(
            select(PanditService)
            .join(Service, PanditService.service_id == Service.id)
            .where(
                PanditService.pandit_id == pandit_id,
                func.lower(Service.service_name) == service_name.strip().lower(),
            )
        )
        return result.scalar_one_or_none()

    async def add_pandit_service(self, pandit_id: UUID, service_id: UUID, price: float) -> PanditService:
        """Stage a new service offering for a pandit."""
        pandit_service = PanditService(pandit_id=pandit_id, service_id=service_id, price=price)
        self.db.add(pandit_service)
        await self.db.flush()
        return pandit_service

    async def delete_pandit_service(self, pandit_service: PanditService) -> None:
        """Remove an offered service from the current session."""
        await self.db.delete(pandit_service)
        await self.db.flush()

    async def replace_pandit_languages(self, pandit_profile: PanditProfile, language_ids: list[UUID]) -> None:
        """Replace the pandit's languages with the provided language ids."""
        for pandit_language in list(pandit_profile.languages):
            await self.db.delete(pandit_language)
        await self.db.flush()

        for language_id in language_ids:
            self.db.add(PanditLanguage(pandit_id=pandit_profile.id, language_id=language_id))
        await self.db.flush()

    async def get_overlapping_slot(self, pandit_id: UUID, start_time, end_time) -> Optional[AvailabilitySlot]:
        """Return an existing slot that overlaps the requested time range."""
        result = await self.db.execute(
            select(AvailabilitySlot).where(
                AvailabilitySlot.pandit_id == pandit_id,
                AvailabilitySlot.start_time < end_time,
                AvailabilitySlot.end_time > start_time,
            )
        )
        return result.scalar_one_or_none()

    async def create_slot(self, pandit_id: UUID, start_time, end_time) -> AvailabilitySlot:
        """Stage a new availability slot for the pandit."""
        slot = AvailabilitySlot(
            pandit_id=pandit_id,
            start_time=start_time,
            end_time=end_time,
            is_booked=False,
        )
        self.db.add(slot)
        await self.db.flush()
        return slot
    
    async def slots_by_pandit_id(self, pandit_id: UUID) -> list[AvailabilitySlot]:
        """Return all slots owned by a pandit ordered by start time."""
        result = await self.db.execute(
            select(AvailabilitySlot).where(AvailabilitySlot.pandit_id == pandit_id).order_by(AvailabilitySlot.start_time).where(AvailabilitySlot.is_booked.is_(False))
        )
        return result.scalars().all()
    async def delete_slot(self,slot: AvailabilitySlot) -> None:
        """Delete a slot from the current session."""
        await self.db.delete(slot)
        await self.db.flush()

    async def get_slot_by_id(self, slot_id: UUID) -> Optional[AvailabilitySlot]:
        """Return one availability slot by id."""
        result = await self.db.execute(select(AvailabilitySlot).where(AvailabilitySlot.id == slot_id))
        return result.scalar_one_or_none()
    
    async def update_slot_time(self,slot:AvailabilitySlot,start_time,end_time) -> AvailabilitySlot:
        """Update the time range of an existing slot."""
        slot.start_time = start_time
        slot.end_time = end_time
        self.db.add(slot)
        await self.db.flush()
        return slot