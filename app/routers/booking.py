from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID       
from app.dependencies import get_current_active_user
from app.database import get_db
from app.repositories import BookingRepository, PanditRepository, UserRepository
from app.services import BookingService
from app.schemas import ApiResponse, BookingSlotResponse   
from app.models import Booking     

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def get_booking_service(db=Depends(get_db))-> Booking:
    """Build the booking service with request-scoped repositories."""
    return BookingService(UserRepository(db), PanditRepository(db), BookingRepository(db))

@router.post("", response_model=ApiResponse[BookingSlotResponse])
async def create_booking(
    pandit_id: UUID,
    service_name: str,
    slot_id: UUID,
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """Create a new booking for the current user with a pandit."""
    booking = await service.create_booking(current_user, pandit_id, service_name, slot_id)
    return ApiResponse(message="Booking created successfully.", data=booking)


@router.get("/user", response_model=ApiResponse[list[BookingSlotResponse]])
async def get_my_bookings(
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """Get all bookings for the current user."""
    bookings = await service.get_bookings_for_user(current_user)
    return ApiResponse(message="Bookings fetched successfully.", data=bookings)

@router.get("/pandit",response_model=ApiResponse[list[BookingSlotResponse]])
async def get_pandit_bookings(
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    bookings=await service.pandit_bookings(current_user)
    return ApiResponse(message="Booking fetched successfully.",data=bookings)

@router.get("/{booking_id}", response_model=ApiResponse[BookingSlotResponse])
async def get_booking_details(
    booking_id: UUID,
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """Get details of a specific booking by ID."""
    booking_details = await service.get_booking_details(booking_id, current_user)
    return ApiResponse(message="Booking details fetched successfully.", data=booking_details)

@router.patch("/{booking_id}/approve", response_model=ApiResponse[BookingSlotResponse])
async def approve_booking(
    booking_id: UUID,
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """Pandit can approve a booking."""
    updated_booking = await service.approve_booking(booking_id, current_user)
    return ApiResponse(message="Booking status updated successfully.", data=updated_booking)

@router.patch("/{booking_id}/reject", response_model=ApiResponse[BookingSlotResponse])
async def reject_booking(
    booking_id: UUID,
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """Pandit can reject a booking."""
    updated_booking = await service.reject_booking(booking_id, current_user)
    return ApiResponse(message="Booking status updated successfully.", data=updated_booking)

@router.patch("/{booking_id}/complete", response_model=ApiResponse[BookingSlotResponse])
async def complete_booking(
    booking_id: UUID,
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """Pandit can complete a booking."""
    updated_booking = await service.complete_booking(booking_id, current_user)
    return ApiResponse(message="Booking status updated successfully.", data=updated_booking)

@router.delete("/{booking_id}", response_model=ApiResponse[None])
async def cancel_booking(
    booking_id: UUID,
    current_user=Depends(get_current_active_user),
    service: BookingService = Depends(get_booking_service),
):
    """User can cancel a booking."""
    await service.cancel_booking(booking_id, current_user)
    return ApiResponse(message="Booking cancelled successfully.", data=None)
