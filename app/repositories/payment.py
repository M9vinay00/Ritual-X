from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AdminRevenue, Booking, Payment
from app.models.enums import PaymentMethod, PaymentStatus


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_booking_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """Return one booking by primary key."""
        return await self.db.get(Booking, booking_id)

    async def get_payment_by_booking_id(self, booking_id: UUID) -> Optional[Payment]:
        """Return one payment for the given booking, if it exists."""
        result = await self.db.execute(select(Payment).where(Payment.booking_id == booking_id))
        return result.scalar_one_or_none()

    async def create_payment(
        self,
        booking: Booking,
        payment_method: PaymentMethod,
        status: PaymentStatus,
    ) -> Payment:
        """Create a new payment and sync the booking payment status."""
        payment = Payment(
            booking_id=booking.id,
            amount=float(booking.amount),
            payment_method=payment_method,
            payment_status=status,
        )
        admin_revenue = AdminRevenue(
            booking_id=booking.id,
            total_amount=float(booking.amount),
            admin_share=float(booking.amount) * 0.20,
            pandit_share=float(booking.amount) * 0.80,
        )
        booking.payment_status = status
        self.db.add(payment)
        self.db.add(admin_revenue)
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_payments_by_user_id(self, user_id: UUID) -> list[Payment]:
        """Return all payments for a user through their bookings."""
        result = await self.db.execute(
            select(Payment)
            .join(Booking, Payment.booking_id == Booking.id)
            .where(Booking.user_id == user_id)
        )
        return list(result.scalars().all())
