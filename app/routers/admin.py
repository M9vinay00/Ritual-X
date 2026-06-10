"""Admin-only API routes for oversight and reporting."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.enums import BookingStatus, PanditProfileStatus
from app.repositories import AdminRepository
from app.schemas import (
    AdminRevenueOverview,
    ApiResponse,
    PaginatedBookingsResponse,
    PaginatedPanditsResponse,
    PaginatedUsersResponse,
    PopularServiceItem,
    RejectPanditRequest,
    TopRatedPanditItem,
    AdminPanditItem,
    AdminUserItem,
)
from app.services import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_service(db=Depends(get_db)) -> AdminService:
    """Build the admin service with a request-scoped repository."""
    return AdminService(AdminRepository(db))


@router.get("/pandits", response_model=ApiResponse[PaginatedPanditsResponse])
async def list_pandits(
    status: PanditProfileStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """List pandit accounts with optional status and pagination filters."""
    data = await service.list_pandits(status=status, page=page, page_size=page_size)
    return ApiResponse(message="Pandits fetched successfully.", data=data)


@router.patch("/pandits/{pandit_id}/approve", response_model=ApiResponse[AdminPanditItem])
async def approve_pandit(
    pandit_id: UUID,
    current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Approve a pandit profile so it can operate on the platform."""
    data = await service.approve_pandit(pandit_id=pandit_id, current_admin=current_admin)
    return ApiResponse(message="Pandit approved successfully.", data=data)


@router.patch("/pandits/{pandit_id}/reject", response_model=ApiResponse[AdminPanditItem])
async def reject_pandit(
    pandit_id: UUID,
    payload: RejectPanditRequest,
    current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Reject a pandit profile and capture the rejection reason."""
    data = await service.reject_pandit(pandit_id=pandit_id, payload=payload, current_admin=current_admin)
    return ApiResponse(message="Pandit rejected successfully.", data=data)


@router.patch("/pandits/{pandit_id}/deactivate", response_model=ApiResponse[AdminPanditItem])
async def deactivate_pandit(
    pandit_id: UUID,
    current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Deactivate a pandit account when business rules allow it."""
    data = await service.deactivate_pandit(pandit_id=pandit_id, current_admin=current_admin)
    return ApiResponse(message="Pandit deactivated successfully.", data=data)


@router.patch("/pandits/{pandit_id}/activate", response_model=ApiResponse[AdminPanditItem])
async def activate_pandit(
    pandit_id: UUID,
    current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Reactivate a previously deactivated pandit account."""
    data = await service.activate_pandit(pandit_id=pandit_id, current_admin=current_admin)
    return ApiResponse(message="Pandit activated successfully.", data=data)


@router.get("/users", response_model=ApiResponse[PaginatedUsersResponse])
async def list_users(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """List end users and pandits with optional text search."""
    data = await service.list_users(search=search, page=page, page_size=page_size)
    return ApiResponse(message="Users fetched successfully.", data=data)


@router.get("/revenue", response_model=ApiResponse[AdminRevenueOverview])
async def get_revenue(
    _current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Return total platform revenue numbers."""
    data = await service.get_revenue_overview()
    return ApiResponse(message="Revenue fetched successfully.", data=data)


@router.get("/pandits/top-rated", response_model=ApiResponse[list[TopRatedPanditItem]])
async def get_top_rated_pandits(
    _current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Return top rated pandits."""
    data = await service.get_top_rated_pandits()
    return ApiResponse(message="Top rated pandits fetched successfully.", data=data)


@router.get("/services/popular", response_model=ApiResponse[list[PopularServiceItem]])
async def get_popular_services(
    _current_admin=Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Return services ranked by number of bookings."""
    data = await service.get_popular_services()
    return ApiResponse(message="Popular services fetched successfully.", data=data)
