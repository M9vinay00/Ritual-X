import uuid

from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: float
    payment_method: str
    status: str
