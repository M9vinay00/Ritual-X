



from datetime import datetime
import uuid

from pydantic import BaseModel


class BookingSlotResponse(BaseModel):
    id: uuid.UUID
    pandit_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    price: float
    service_name: str
    is_booked: bool
    status: str