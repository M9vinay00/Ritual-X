from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RejectPanditRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class AdminPanditItem(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    city_name: Optional[str] = None
    status: str
    is_active: bool
    experience_years: int
    avg_rating: float
    rating_count: int
    rejection_reason: Optional[str] = None
    created_at: datetime


class PaginatedPanditsResponse(BaseModel):
    items: list[AdminPanditItem]
    total: int
    page: int
    page_size: int


class AdminUserItem(BaseModel):
    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    city_name: Optional[str] = None
    preferred_language_name: Optional[str] = None
    is_active: bool
    is_super_admin: bool
    created_at: datetime


class PaginatedUsersResponse(BaseModel):
    items: list[AdminUserItem]
    total: int
    page: int
    page_size: int


class AdminBookingItem(BaseModel):
    id: UUID
    user_name: str
    user_email: str
    pandit_name: str
    pandit_email: str
    service_name: str
    start_time: datetime
    end_time: datetime
    booking_date: date
    status: str
    payment_status: str
    amount: float
    admin_share: float
    pandit_share: float
    created_at: datetime


class PaginatedBookingsResponse(BaseModel):
    items: list[AdminBookingItem]
    total: int
    page: int
    page_size: int


class AdminRevenueOverview(BaseModel):
    total_bookings: int
    total_gross_revenue: float
    total_platform_revenue: float
    total_pandit_payout: float


class TopRatedPanditItem(BaseModel):
    pandit_id: UUID
    name: str
    city_name: Optional[str] = None
    avg_rating: float
    rating_count: int
    completed_bookings: int


class PopularServiceItem(BaseModel):
    service_name: str
    booking_count: int
    total_revenue: float
