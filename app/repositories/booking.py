from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AvailabilitySlot, Booking, PanditService, Service
from app.models.enums import BookingStatus
from sqlalchemy.orm import selectinload

class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_slot_by_id(self, slot_id: UUID) -> Optional[AvailabilitySlot]:
        """Return one availability slot by id."""
        result = await self.db.execute(select(AvailabilitySlot).where(AvailabilitySlot.id == slot_id))
        return result.scalar_one_or_none()

    async def get_booking_by_slot_id(self, slot_id: UUID) -> Optional[Booking]:
        """Return an existing booking for the given slot, if any."""
        result = await self.db.execute(select(Booking).where(Booking.slot_id == slot_id))
        return result.scalar_one_or_none()

    async def get_pandit_service_by_name(self, pandit_id: UUID, service_name: str) -> Optional[PanditService]:
        """Return the offered service mapping for the selected pandit and service name."""
        statement = (
            select(PanditService)
            .join(Service, PanditService.service_id == Service.id)
            .options(selectinload(PanditService.service))
            .where(
                PanditService.pandit_id == pandit_id,
                func.lower(Service.service_name) == service_name.strip().lower(),
            )
        )
        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def create_booking(
        self,
        user_id: UUID,
        pandit_id: UUID,
        service_id: UUID,
        slot_id: UUID,
        start_time: datetime,
        end_time: datetime,
        amount: float,
        slot: AvailabilitySlot,
        status: BookingStatus = BookingStatus.PENDING,
    ) -> Booking:
        """Create a new booking for a user with a pandit."""
        slot.is_booked = True
        new_booking = Booking(
            user_id=user_id,
            pandit_id=pandit_id,
            service_id=service_id,
            slot_id=slot_id,
            start_time=start_time, 
            end_time=end_time,    
            status=status,
            amount=amount,
        )
        self.db.add(slot)
        self.db.add(new_booking)
        await self.db.commit()
        await self.db.refresh(new_booking)
        return new_booking
  

    async def get_bookings(self, user_id: UUID):
        """Return all bookings for a given user."""
        result = await self.db.execute(
            select(Booking, Service.service_name)
            .join(Service, Booking.service_id == Service.id)
            .where(Booking.user_id == user_id)
        )
        return result.all()
    
    async def booking_details(self,booking_id:UUID):
        result = await self.db.execute(
            select(Booking, Service.service_name)
            .join(Service, Booking.service_id == Service.id)
            .where(Booking.id == booking_id)
        )
        return result.one_or_none()
    
    async def pandit_bookings(self,pandit_id:UUID):
        """Return all bookings for a given user."""

        result =await self.db.execute(
            select(Booking,Service.service_name).join(Service,Booking.service_id==Service.id).where(Booking.pandit_id==pandit_id)

        )
        return result.all()
    
    async def pandit_approval(self,booking_id:UUID,status:BookingStatus):
        booking = await self.db.get(Booking,booking_id)
        if not booking:
            return None
        booking.status=status
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking
    
    async def pandit_rejection(self,booking_id:UUID,status:BookingStatus):
        booking = await self.db.get(Booking,booking_id)
        if not booking:
            return None
        booking.status=status
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def get_booking_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """Return one booking by primary key."""
        return await self.db.get(Booking, booking_id)
    
    async def complete_booking(self,booking_id:UUID,status:BookingStatus):
        booking = await self.db.get(Booking,booking_id)
        if not booking:
            return None
        booking.status=status
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking
    
    async def cancel_booking(self,booking_id:UUID,status:BookingStatus):

        booking = await self.db.get(Booking,booking_id)
        if not booking:
            return None
        booking.status = status
        if booking.slot_id:
            slot = await self.db.get(AvailabilitySlot, booking.slot_id)
            if slot:
                slot.is_booked = False
                self.db.add(slot)
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking      
     
