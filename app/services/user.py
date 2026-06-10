"""Business logic for user self-service profile operations."""

from fastapi import HTTPException, status

from app.models.enums import RoleName
from app.repositories import UserRepository
from app.schemas import ChangeLanguageRequest, UpdateMeRequest, UserMeResponse


class UserService:
    """Handle profile changes for regular users and admin lookups."""

    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.db = repo.db

    async def update_me(self, current_user, payload: UpdateMeRequest) -> UserMeResponse:
        """Update the authenticated user's editable profile fields."""
        user = await self.repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        city = None
        if payload.city_name is not None:
            city = await self.repo.get_city_by_name(payload.city_name)
            if not city:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found.")

        language = None
        if payload.preferred_language_name is not None:
            language = await self.repo.get_language_by_name(payload.preferred_language_name)
            if not language:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found.")

        user.name = payload.name
        user.city_id = city.id if city else None
        user.preferred_language_id = language.id if language else None
        await self.db.commit()
        updated_user = await self.repo.get_user_by_id(user.id)
        return self.serialize_user(updated_user)

    async def change_language(self, current_user, payload: ChangeLanguageRequest) -> UserMeResponse:
        """Allow a regular user to override the preferred language manually."""
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only user can change language manually.")

        user = await self.repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        language = await self.repo.get_language_by_name(payload.preferred_language_name)
        if not language:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found.")

        user.preferred_language_id = language.id
        await self.db.commit()
        updated_user = await self.repo.get_user_by_id(user.id)
        return self.serialize_user(updated_user)

    async def get_user_by_id(self, user_id) -> UserMeResponse:
        """Fetch a user by id and serialize it for API output."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return self.serialize_user(user)

    @staticmethod
    def serialize_user(user) -> UserMeResponse:
        """Convert a user model into the user profile response schema."""
        pandit_profile = user.pandit_profile
        return UserMeResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role.role_name,
            is_active=user.is_active,
            is_super_admin=user.is_super_admin,
            city_name=user.city.city_name if user.city else None,
            preferred_language_name=user.preferred_language.language_name if user.preferred_language else None,
            pandit_status=pandit_profile.status.value if pandit_profile else None,
            pandit_profile_active=pandit_profile.is_active if pandit_profile else None,
        )
