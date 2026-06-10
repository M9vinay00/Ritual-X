"""User account management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_active_user, get_current_admin
from app.repositories import UserRepository
from app.schemas import ApiResponse, ChangeLanguageRequest, UpdateMeRequest, UserMeResponse
from app.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db=Depends(get_db)) -> UserService:
    """Build the user service with a request-scoped repository."""
    return UserService(UserRepository(db))


@router.put("/me", response_model=ApiResponse[UserMeResponse])
async def update_me(
    payload: UpdateMeRequest,
    current_user=Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
):
    """Update the authenticated user's profile information."""
    user = await service.update_me(current_user, payload)
    return ApiResponse(message="User profile updated successfully.", data=user)


@router.patch("/me/language", response_model=ApiResponse[UserMeResponse])
async def change_language(
    payload: ChangeLanguageRequest,
    current_user=Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
):
    """Change the authenticated user's preferred language."""
    user = await service.change_language(current_user, payload)
    return ApiResponse(message="Preferred language updated successfully.", data=user)


@router.get("/{user_id}", response_model=ApiResponse[UserMeResponse])
async def get_user_by_id(
    user_id: UUID,
    _current_admin=Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    """Fetch a user by id for admin use."""
    user = await service.get_user_by_id(user_id)
    return ApiResponse(message="User fetched successfully.", data=user)
