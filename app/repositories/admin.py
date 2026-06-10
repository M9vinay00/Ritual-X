"""Database queries that power admin moderation and reporting workflows."""

from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AdminRevenue, Booking, PanditProfile, Role, Service, User
from app.models.enums import BookingStatus, PanditProfileStatus


class AdminRepository:
    """Encapsulate admin-facing read and write queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _paginate(self, statement, *, page: int, page_size: int):
        """Apply a limit/offset page window and return rows with total count."""
        total = await self.db.scalar(select(func.count()).select_from(statement.order_by(None).subquery()))
        result = await self.db.execute(statement.limit(page_size).offset((page - 1) * page_size))
        return result.scalars().all(), int(total or 0)

    async def get_pandit_profile_by_id(self, pandit_id: UUID):
        """Return a pandit profile with related user and city data."""
        statement = (
            select(PanditProfile)
            .options(
                selectinload(PanditProfile.user).selectinload(User.city),
                selectinload(PanditProfile.user).selectinload(User.role),
            )
            .where(PanditProfile.id == pandit_id)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def list_pandits(self, *, status: PanditProfileStatus | None, page: int, page_size: int):
        """Return paginated pandit profiles for the admin panel."""
        statement = (
            select(PanditProfile)
            .join(User, PanditProfile.user_id == User.id)
            .options(
                selectinload(PanditProfile.user).selectinload(User.city),
                selectinload(PanditProfile.user).selectinload(User.role),
            )
            .order_by(PanditProfile.created_at.desc())
        )
        if status:
            statement = statement.where(PanditProfile.status == status)
        return await self._paginate(statement, page=page, page_size=page_size)

    async def has_open_bookings(self, pandit_id: UUID) -> bool:
        """Check whether a pandit still has pending or confirmed bookings."""
        statement = select(func.count(Booking.id)).where(
            Booking.pandit_id == pandit_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        )
        total = await self.db.scalar(statement)
        return bool(total)

    async def list_users(self, *, search: str | None, page: int, page_size: int):
        """Return paginated users with optional text search."""
        statement = (
            select(User)
            .join(Role, User.role_id == Role.id)
            .options(
                selectinload(User.role),
                selectinload(User.city),
                selectinload(User.preferred_language),
                selectinload(User.pandit_profile),
            )
            .order_by(User.created_at.desc())
        )
        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    User.name.ilike(pattern),
                    User.email.ilike(pattern),
                    User.phone.ilike(pattern),
                )
            )
        return await self._paginate(statement, page=page, page_size=page_size)

    async def get_user_by_id(self, user_id: UUID):
        """Return one user with the related profile data needed by admins."""
        statement = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.city),
                selectinload(User.preferred_language),
                selectinload(User.pandit_profile),
            )
            .where(User.id == user_id)
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_revenue_overview(self):
        """Return total bookings and revenue split values."""
        statement = select(
            func.count(AdminRevenue.id),
            func.coalesce(func.sum(AdminRevenue.total_amount), 0.0),
            func.coalesce(func.sum(AdminRevenue.admin_share), 0.0),
            func.coalesce(func.sum(AdminRevenue.pandit_share), 0.0),
        )
        result = await self.db.execute(statement)
        return result.one()

    async def get_top_rated_pandits(self):
        """Return top rated pandits with at least five ratings."""
        completed_bookings = (
            select(
                Booking.pandit_id.label("pandit_id"),
                func.count(Booking.id).label("completed_bookings"),
            )
            .where(Booking.status == BookingStatus.COMPLETED)
            .group_by(Booking.pandit_id)
            .subquery()
        )

        statement = (
            select(
                PanditProfile,
                func.coalesce(completed_bookings.c.completed_bookings, 0),
            )
            .join(User, PanditProfile.user_id == User.id)
            .outerjoin(completed_bookings, completed_bookings.c.pandit_id == PanditProfile.id)
            .options(selectinload(PanditProfile.user).selectinload(User.city))
            .where(PanditProfile.rating_count >= 5)
            .order_by(PanditProfile.avg_rating.desc(), PanditProfile.rating_count.desc())
            .limit(10)
        )
        result = await self.db.execute(statement)
        return result.all()

    async def get_popular_services(self):
        """Return services ranked by booking count."""
        statement = (
            select(
                Service.service_name,
                func.count(Booking.id).label("booking_count"),
                func.coalesce(func.sum(Booking.amount), 0.0).label("total_revenue"),
            )
            .join(Booking, Booking.service_id == Service.id)
            .group_by(Service.id, Service.service_name)
            .order_by(func.count(Booking.id).desc(), Service.service_name.asc())
        )
        result = await self.db.execute(statement)
        return result.all()
