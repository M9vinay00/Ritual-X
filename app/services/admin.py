"""Business logic for admin dashboards and moderation workflows."""

from datetime import date
from uuid import UUID

from fastapi import HTTPException, status

from app.models.enums import BookingStatus, PanditProfileStatus, RoleName
from app.repositories import AdminRepository
from app.schemas import (
    AdminBookingItem,
    AdminPanditItem,
    AdminRevenueOverview,
    AdminUserItem,
    PaginatedBookingsResponse,
    PaginatedPanditsResponse,
    PaginatedUsersResponse,
    PopularServiceItem,
    RejectPanditRequest,
    TopRatedPanditItem,
)


class AdminService:
    """Handle admin-only operations on users, pandits, and reporting views."""

    def __init__(self, repo: AdminRepository):
        self.repo = repo
        self.db = repo.db

    async def list_pandits(self, *, status: PanditProfileStatus | None, page: int, page_size: int) -> PaginatedPanditsResponse:
        """Return paginated pandit accounts for the admin panel."""
        pandits, total = await self.repo.list_pandits(status=status, page=page, page_size=page_size)
        return PaginatedPanditsResponse(
            items=[self.serialize_pandit_item(pandit) for pandit in pandits],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def approve_pandit(self, *, pandit_id: UUID, current_admin) -> AdminPanditItem:
        """Approve a pandit profile and clear any prior rejection note."""
        pandit_profile = await self._get_pandit_or_404(pandit_id)
        pandit_profile.status = PanditProfileStatus.APPROVED
        pandit_profile.is_active = True
        pandit_profile.rejection_reason = None
        pandit_profile.updated_by = current_admin.id
        await self.db.commit()
        refreshed = await self.repo.get_pandit_profile_by_id(pandit_id)
        return self.serialize_pandit_item(refreshed)

    async def reject_pandit(self, *, pandit_id: UUID, payload: RejectPanditRequest, current_admin) -> AdminPanditItem:
        """Reject a pandit profile with a reason visible to admins."""
        pandit_profile = await self._get_pandit_or_404(pandit_id)
        pandit_profile.status = PanditProfileStatus.REJECTED
        pandit_profile.rejection_reason = payload.reason.strip()
        pandit_profile.updated_by = current_admin.id
        await self.db.commit()
        refreshed = await self.repo.get_pandit_profile_by_id(pandit_id)
        return self.serialize_pandit_item(refreshed)

    async def deactivate_pandit(self, *, pandit_id: UUID, current_admin) -> AdminPanditItem:
        """Deactivate a pandit unless active bookings still depend on them."""
        pandit_profile = await self._get_pandit_or_404(pandit_id)
        if await self.repo.has_open_bookings(pandit_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pandit cannot be deactivated while pending or confirmed bookings exist.",
            )
        pandit_profile.is_active = False
        pandit_profile.updated_by = current_admin.id
        await self.db.commit()
        refreshed = await self.repo.get_pandit_profile_by_id(pandit_id)
        return self.serialize_pandit_item(refreshed)

    async def activate_pandit(self, *, pandit_id: UUID, current_admin) -> AdminPanditItem:
        """Reactivate a pandit account."""
        pandit_profile = await self._get_pandit_or_404(pandit_id)
        pandit_profile.is_active = True
        pandit_profile.updated_by = current_admin.id
        await self.db.commit()
        refreshed = await self.repo.get_pandit_profile_by_id(pandit_id)
        return self.serialize_pandit_item(refreshed)

    async def list_users(self, *, search: str | None, page: int, page_size: int) -> PaginatedUsersResponse:
        """Return paginated users for the admin panel."""
        users, total = await self.repo.list_users(search=search, page=page, page_size=page_size)
        return PaginatedUsersResponse(
            items=[self.serialize_user_item(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_revenue_overview(self) -> AdminRevenueOverview:
        """Return aggregate revenue numbers for the admin dashboard."""
        total_bookings, total_gross_revenue, total_platform_revenue, total_pandit_payout = (
            await self.repo.get_revenue_overview()
        )
        return AdminRevenueOverview(
            total_bookings=int(total_bookings or 0),
            total_gross_revenue=float(total_gross_revenue or 0),
            total_platform_revenue=float(total_platform_revenue or 0),
            total_pandit_payout=float(total_pandit_payout or 0),
        )

    async def get_top_rated_pandits(self) -> list[TopRatedPanditItem]:
        """Return top rated pandits who have enough ratings."""
        rows = await self.repo.get_top_rated_pandits()
        return [
            TopRatedPanditItem(
                pandit_id=pandit.id,
                name=pandit.user.name,
                city_name=pandit.user.city.city_name if pandit.user and pandit.user.city else None,
                avg_rating=float(pandit.avg_rating),
                rating_count=pandit.rating_count,
                completed_bookings=int(completed_bookings or 0),
            )
            for pandit, completed_bookings in rows
        ]

    async def get_popular_services(self) -> list[PopularServiceItem]:
        """Return services ranked by bookings."""
        rows = await self.repo.get_popular_services()
        return [
            PopularServiceItem(
                service_name=service_name,
                booking_count=int(booking_count or 0),
                total_revenue=float(total_revenue or 0),
            )
            for service_name, booking_count, total_revenue in rows
        ]

    async def _get_pandit_or_404(self, pandit_id: UUID):
        """Fetch a pandit profile or raise a not-found error."""
        pandit_profile = await self.repo.get_pandit_profile_by_id(pandit_id)
        if not pandit_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pandit not found.")
        return pandit_profile

    @staticmethod
    def serialize_pandit_item(pandit_profile) -> AdminPanditItem:
        """Convert a pandit profile model into the admin response schema."""
        return AdminPanditItem(
            id=pandit_profile.id,
            user_id=pandit_profile.user_id,
            name=pandit_profile.user.name,
            email=pandit_profile.user.email,
            phone=pandit_profile.user.phone,
            city_name=pandit_profile.user.city.city_name if pandit_profile.user.city else None,
            status=pandit_profile.status.value,
            is_active=pandit_profile.is_active,
            experience_years=pandit_profile.experience_years,
            avg_rating=float(pandit_profile.avg_rating),
            rating_count=pandit_profile.rating_count,
            rejection_reason=pandit_profile.rejection_reason,
            created_at=pandit_profile.created_at,
        )

    @staticmethod
    def serialize_user_item(user) -> AdminUserItem:
        """Convert a user model into the admin response schema."""
        return AdminUserItem(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role.role_name,
            city_name=user.city.city_name if user.city else None,
            preferred_language_name=user.preferred_language.language_name if user.preferred_language else None,
            is_active=user.is_active,
            is_super_admin=user.is_super_admin,
            created_at=user.created_at,
        )

  
