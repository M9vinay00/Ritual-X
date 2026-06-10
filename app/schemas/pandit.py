import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PanditSearchItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    city_name: Optional[str] = None
    experience_years: int
    description: Optional[str] = None
    avg_rating: float
    rating_count: int
    language_names: list[str] = Field(default_factory=list)
    service_names: list[str] = Field(default_factory=list)


class PanditServiceItem(BaseModel):
    service_name: str
    price: float


class PanditRatingItem(BaseModel):
    rating_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    rating: int
    review: Optional[str] = None


class PanditProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    email: str
    phone: Optional[str] = None
    city_name: Optional[str] = None
    experience_years: int
    description: Optional[str] = None
    status: str
    is_active: bool
    avg_rating: float
    rating_count: int
    language_names: list[str] = Field(default_factory=list)
    services: list[PanditServiceItem] = Field(default_factory=list)
    ratings: list[PanditRatingItem] = Field(default_factory=list)


class UpdatePanditProfileRequest(BaseModel):
    city_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    experience_years: int = Field(ge=0, le=80)
    description: Optional[str] = Field(default=None, max_length=2000)
    language_names: list[str] = Field(default_factory=list)


class AddPanditServiceRequest(BaseModel):
    service_name: str = Field(min_length=2, max_length=120)
    price: float = Field(gt=0)


class CreateAvailabilitySlotRequest(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailabilitySlotResponse(BaseModel):
    id: uuid.UUID
    pandit_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    is_booked: bool


class PanditEarningsResponse(BaseModel):
    pandit_id: uuid.UUID
    total_earned: float
    total_bookings: int
    completed_bookings: int
    pending_bookings: int
