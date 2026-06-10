from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Booking, PanditProfile, Rating, User


class RatingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_booking_by_id(self, booking_id: UUID) -> Optional[Booking]:
        result = await self.db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()

    async def get_rating_by_booking_id(self, booking_id: UUID) -> Optional[Rating]:
        statement = (
            select(Rating)
            .options(selectinload(Rating.user))
            .where(Rating.booking_id == booking_id)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def create_rating(self, user_id: UUID, pandit_id: UUID, booking_id: UUID, rating: int, review: str | None):
        pandit_profile = await self.db.get(PanditProfile, pandit_id)
        new_rating = Rating(
            user_id=user_id,
            pandit_id=pandit_id,
            booking_id=booking_id,
            rating=rating,
            review=review,
        )

        if pandit_profile:
            pandit_profile.total_rating += rating
            pandit_profile.rating_count += 1
            pandit_profile.avg_rating = pandit_profile.total_rating / pandit_profile.rating_count
            self.db.add(pandit_profile)

        self.db.add(new_rating)
        await self.db.commit()
        await self.db.refresh(new_rating)
        await self.db.refresh(new_rating, attribute_names=["user"])
        return new_rating

    async def get_ratings_by_pandit_id(self, pandit_id: UUID) -> list[Rating]:
        statement = (
            select(Rating)
            .options(selectinload(Rating.user))
            .where(Rating.pandit_id == pandit_id)
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_ratings_by_user_id(self, user_id: UUID) -> list[Rating]:
        statement = (
            select(Rating)
            .options(selectinload(Rating.user))
            .where(Rating.user_id == user_id)
        )
        result = await self.db.execute(statement)
        return result.scalars().all()
