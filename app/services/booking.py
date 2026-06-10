from fastapi import HTTPException, status
from uuid import UUID

from app.models.enums import RoleName,BookingStatus
from app.schemas.booking import BookingSlotResponse
from app.repositories.booking import BookingRepository
from app.repositories.pandit import PanditRepository
from app.repositories.user import UserRepository




class BookingService:
    def __init__(self, user_repo: UserRepository, pandit_repo: PanditRepository, booking_repo: BookingRepository):
        self.user_repo = user_repo
        self.pandit_repo = pandit_repo
        self.booking_repo = booking_repo


    async def _get_own_pandit_profile(self, current_user):
        """Validate pandit access and load the caller's linked profile."""
        if current_user.role.role_name != RoleName.PANDIT.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pandit access required.")

        pandit_profile = await self.pandit_repo.get_pandit_profile_by_user_id(current_user.id)
        if not pandit_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pandit profile not found.")
        if not pandit_profile.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pandit account is deactivated.")
        return pandit_profile

    async def create_booking(
        self,
        current_user,
        pandit_id: UUID,
        service_name: str,
        slot_id: UUID
    ) -> BookingSlotResponse:
        """Create a new booking for the current user with a pandit."""

        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only user can create bookings."
            )

        user = await self.user_repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        slot = await self.booking_repo.get_slot_by_id(slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found."
            )

        if slot.pandit_id != pandit_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This slot does not belong to the selected pandit."
            )

        existing_booking = await self.booking_repo.get_booking_by_slot_id(slot_id)
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This slot is already booked."
            )

        pandit_service = await self.booking_repo.get_pandit_service_by_name(pandit_id, service_name)
        if not pandit_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected service is not offered by this pandit."
            )

        new_booking = await self.booking_repo.create_booking(
            user_id=current_user.id,
            pandit_id=pandit_id,
            service_id=pandit_service.service_id,
            slot_id=slot_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            amount=float(pandit_service.price),
            slot=slot,
        )

        return BookingSlotResponse(
            id=new_booking.id,
            pandit_id=new_booking.pandit_id,
            start_time=new_booking.start_time,
            end_time=new_booking.end_time,
            price=float(pandit_service.price),
            service_name=pandit_service.service.service_name,
            is_booked=True,
            status=new_booking.status.value,
        )
    

    async def get_bookings_for_user(self, current_user) -> list[BookingSlotResponse]:
        """Return all bookings for the current user."""
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only users can view their bookings."
            )

        user = await self.user_repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        bookings = await self.booking_repo.get_bookings(current_user.id)
        return [
            BookingSlotResponse(
                id=booking.id,
                pandit_id=booking.pandit_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                price=float(booking.amount),
                service_name=service_name,
                is_booked=True,
                status=booking.status.value,
            )
            for booking, service_name in bookings
        ]
    
    async def get_booking_details(self, booking_id: UUID, current_user) -> BookingSlotResponse:
        """Return detailed information for a specific booking."""
        
        booking = await self.booking_repo.booking_details(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )
        booking, service_name = booking
        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this booking."
            )
        return BookingSlotResponse(
            id=booking.id,
            pandit_id=booking.pandit_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            price=float(booking.amount),
            service_name=service_name,
            is_booked=True,
            status=booking.status.value,
        )
    
    async def pandit_bookings(self,current_user)->list[BookingSlotResponse]:
        pandit_profile=await self._get_own_pandit_profile(current_user)
        if not pandit_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pandit not found."
            )
        bookings=await self.booking_repo.pandit_bookings(pandit_profile.id)
        return [
            BookingSlotResponse(
                id=booking.id,
                pandit_id=booking.pandit_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                price=float(booking.amount),
                service_name=service_name,
                is_booked=True,
                status=booking.status.value,
            )
            for booking, service_name in bookings
        ]
    
    async def approve_booking(self,booking_id:UUID,current_user):
        pandit_profile=await self._get_own_pandit_profile(current_user)
        if not pandit_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pandit not found."
            )
        booking=await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        if booking.pandit_id != pandit_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this booking."
            )

        if booking.status.value == BookingStatus.CONFIRMED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already confirmed."
            )
        if booking.status.value == BookingStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already completed."
            )

        booking=await self.booking_repo.pandit_approval(booking_id,status=BookingStatus.CONFIRMED)
        return BookingSlotResponse(
                id=booking.id,
                pandit_id=booking.pandit_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                price=float(booking.amount),
                service_name="",  
                is_booked=True,
                status=booking.status.value,
            )
    
    async def reject_booking(self,booking_id:UUID,current_user):
        pandit_profile=await self._get_own_pandit_profile(current_user)
        if not pandit_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pandit not found."
            )
        booking=await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        if booking.pandit_id != pandit_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this booking."
            )

        if booking.status.value == BookingStatus.REJECTED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already rejected."
            )
        if booking.status.value == BookingStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already completed."
            )

        booking=await self.booking_repo.pandit_rejection(booking_id,status=BookingStatus.REJECTED)
        return BookingSlotResponse(
                id=booking.id,
                pandit_id=booking.pandit_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                price=float(booking.amount),
                service_name="",  
                is_booked=True,
                status=booking.status.value,
            )
    async def complete_booking(self,booking_id:UUID,current_user):
        pandit_profile=await self._get_own_pandit_profile(current_user)
        if not pandit_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pandit not found."
            )
        booking=await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        if booking.pandit_id != pandit_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this booking."
            )

        if booking.status.value == BookingStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already completed."
            )
        if booking.status.value != BookingStatus.CONFIRMED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only confirmed bookings can be marked as completed."
            )

        booking=await self.booking_repo.complete_booking(booking_id,status=BookingStatus.COMPLETED)
        return BookingSlotResponse(
                id=booking.id,
                pandit_id=booking.pandit_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                price=float(booking.amount),
                service_name="",  
                is_booked=True,
                status=booking.status.value,
            )
    async def cancel_booking(self,booking_id:UUID,current_user):
        booking=await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )
        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel this booking."
            )
        if booking.status.value == BookingStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already cancelled."
            )
        if booking.status.value == BookingStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="this booking is already completed."
            )

        cancelled_booking=await self.booking_repo.cancel_booking(booking_id,status=BookingStatus.CANCELLED)
        return BookingSlotResponse(
                id=cancelled_booking.id,
                pandit_id=cancelled_booking.pandit_id,
                start_time=cancelled_booking.start_time,
                end_time=cancelled_booking.end_time,
                price=float(cancelled_booking.amount),
                service_name="",  
                is_booked=False,
                status=cancelled_booking.status.value,
            )

    

        
