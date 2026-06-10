from uuid import UUID

from fastapi import HTTPException, status

from app.models.enums import BookingStatus, PaymentMethod, PaymentStatus, RoleName
from app.repositories.payment import PaymentRepository
from app.repositories.user import UserRepository
from app.schemas.payment import PaymentResponse


class Paymentservice:
    def __init__(self, user_repo: UserRepository, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo
        self.user_repo = user_repo

    async def create_payment(
        self,
        current_user,
        booking_id: UUID,
    ) -> PaymentResponse:
        """Create a cash payment for the current user's booking."""
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only user can create payments.",
            )

        user = await self.user_repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        booking = await self.payment_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to pay for this booking.",
            )

        if booking.status.value == BookingStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not allowed for this booking because it is cancelled.",
            )
        if booking.status.value == BookingStatus.REJECTED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not allowed for this booking because it is rejected.",
            )
        if booking.status.value == BookingStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not allowed for this booking because it is pending confirmation.",
            )
        if booking.status.value == BookingStatus.CONFIRMED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not allowed for this booking because it is not completed.",
            )

        existing_payment = await self.payment_repo.get_payment_by_booking_id(booking_id)
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already exists for this booking.",
            )

        payment = await self.payment_repo.create_payment(
            booking=booking,
            payment_method=PaymentMethod.CASH,
            status=PaymentStatus.PAID,
        )

        return PaymentResponse(
            id=payment.id,
            booking_id=payment.booking_id,
            amount=float(payment.amount),
            payment_method=payment.payment_method.value,
            status=payment.payment_status.value,
        )

    async def get_payments_for_user(self, current_user) -> list[PaymentResponse]:
        """Return all payments for the current user."""
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only users can view their payments.",
            )

        user = await self.user_repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        payments = await self.payment_repo.get_payments_by_user_id(current_user.id)
        return [
            PaymentResponse(
                id=payment.id,
                booking_id=payment.booking_id,
                amount=float(payment.amount),
                payment_method=payment.payment_method.value,
                status=payment.payment_status.value,
            )
            for payment in payments
        ]
