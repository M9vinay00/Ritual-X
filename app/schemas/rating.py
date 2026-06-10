import uuid
from typing import Optional

from pydantic import BaseModel, Field


class CreateRatingRequest(BaseModel):
    booking_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=1000)


class RatingResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    user_id: uuid.UUID
    pandit_id: uuid.UUID
    user_name: str
    rating: int
    review: Optional[str] = None
