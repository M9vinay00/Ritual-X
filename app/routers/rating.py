from uuid import UUID

from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_active_user
from app.repositories import PanditRepository, RatingRepository, UserRepository
from app.schemas import ApiResponse, CreateRatingRequest, RatingResponse
from app.services import RatingService

router = APIRouter(tags=["Ratings"])


def get_rating_service(db=Depends(get_db)) -> RatingService:
    return RatingService(UserRepository(db), PanditRepository(db), RatingRepository(db))


@router.post("/ratings", response_model=ApiResponse[RatingResponse])
async def create_rating(
    payload: CreateRatingRequest,
    current_user=Depends(get_current_active_user),
    service: RatingService = Depends(get_rating_service),
):
    rating = await service.create_rating(current_user, payload)
    return ApiResponse(message="Rating submitted successfully.", data=rating)


@router.get("/pandits/{pandit_id}/ratings", response_model=ApiResponse[list[RatingResponse]])
async def get_pandit_ratings(
    pandit_id: UUID,
    service: RatingService = Depends(get_rating_service),
):
    ratings = await service.get_pandit_ratings(pandit_id)
    return ApiResponse(message="Ratings fetched successfully.", data=ratings)


@router.get("/ratings/me", response_model=ApiResponse[list[RatingResponse]])
async def get_my_ratings(
    current_user=Depends(get_current_active_user),
    service: RatingService = Depends(get_rating_service),
):
    ratings = await service.get_my_ratings(current_user)
    return ApiResponse(message="Your ratings fetched successfully.", data=ratings)
