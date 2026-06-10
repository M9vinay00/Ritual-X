from uuid import UUID

from fastapi import HTTPException, status

from app.models.enums import BookingStatus, RoleName
from app.repositories.pandit import PanditRepository
from app.repositories.rating import RatingRepository
from app.repositories.user import UserRepository
from app.schemas.rating import CreateRatingRequest, RatingResponse


class RatingService:
    def __init__(self, user_repo: UserRepository, pandit_repo: PanditRepository, rating_repo: RatingRepository):
        self.user_repo = user_repo
        self.pandit_repo = pandit_repo
        self.rating_repo = rating_repo

    async def create_rating(self, current_user, payload: CreateRatingRequest) -> RatingResponse:
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only user can submit ratings."
            )

        user = await self.user_repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        booking = await self.rating_repo.get_booking_by_id(payload.booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to rate this booking."
            )

        if booking.status.value != BookingStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating is allowed only for completed bookings."
            )

        existing_rating = await self.rating_repo.get_rating_by_booking_id(payload.booking_id)
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating already submitted for this booking."
            )

        rating = await self.rating_repo.create_rating(
            user_id=current_user.id,
            pandit_id=booking.pandit_id,
            booking_id=payload.booking_id,
            rating=payload.rating,
            review=payload.review,
        )

        return self.serialize_rating(rating)

    async def get_pandit_ratings(self, pandit_id: UUID) -> list[RatingResponse]:
        pandit_profile = await self.pandit_repo.get_public_pandit_by_id(pandit_id)
        if not pandit_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pandit not found."
            )

        ratings = await self.rating_repo.get_ratings_by_pandit_id(pandit_id)
        return [self.serialize_rating(rating) for rating in ratings]

    async def get_my_ratings(self, current_user) -> list[RatingResponse]:
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only users can view their ratings."
            )

        user = await self.user_repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        ratings = await self.rating_repo.get_ratings_by_user_id(current_user.id)
        return [self.serialize_rating(rating) for rating in ratings]

    @staticmethod
    def serialize_rating(rating) -> RatingResponse:
        return RatingResponse(
            id=rating.id,
            booking_id=rating.booking_id,
            user_id=rating.user_id,
            pandit_id=rating.pandit_id,
            user_name=rating.user.name,
            rating=rating.rating,
            review=rating.review,
        )
