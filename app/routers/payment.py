from uuid import UUID

from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_active_user
from app.repositories import PaymentRepository, UserRepository
from app.schemas import ApiResponse, PaymentResponse
from app.services import Paymentservice


router = APIRouter(prefix="/payments", tags=["Payments"])


def get_payment_service(db=Depends(get_db)):
    """Build the payment service with request-scoped repositories."""
    return Paymentservice(UserRepository(db), PaymentRepository(db))


@router.post("", response_model=ApiResponse[PaymentResponse])
async def create_payment(
    booking_id: UUID,
    current_user=Depends(get_current_active_user),
    service: Paymentservice = Depends(get_payment_service),
):
    """Create a cash payment for the current user's booking."""
    payment = await service.create_payment(current_user=current_user, booking_id=booking_id)
    return ApiResponse(message="Payment created successfully.", data=payment)


@router.get("/user", response_model=ApiResponse[list[PaymentResponse]])
async def get_my_payments(
    current_user=Depends(get_current_active_user),
    service: Paymentservice = Depends(get_payment_service),
):
    """Get all payments for the current user."""
    payments = await service.get_payments_for_user(current_user)
    return ApiResponse(message="Payments fetched successfully.", data=payments)
