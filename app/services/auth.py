"""Business logic for registration, authentication, and password recovery."""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.security import (
    create_access_token,
    create_password_reset_token,
    hash_password,
    hash_password_reset_token,
    verify_password_reset_token,
    verify_password,
)
from app.models.enums import PanditProfileStatus, RoleName
from app.repositories import AuthRepository
from app.schemas import (
    ForgotPasswordRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)


class AuthService:
    """Coordinate auth rules on top of repository access and token helpers."""

    def __init__(self, repo: AuthRepository):
        self.repo = repo
        self.db = repo.db
    
    async def register(self, payload: RegisterRequest) -> UserResponse:
        """Register a new account and create a linked pandit profile when needed."""
        try:
            if payload.role == RoleName.ADMIN.value:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin registration is not allowed.")

            role_name = RoleName(payload.role)
            existing_user = await self.repo.get_user_by_email(payload.email)
            if existing_user:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.")

            if payload.phone:
                existing_phone_user = await self.repo.get_user_by_phone(payload.phone)
                if existing_phone_user:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number is already registered.")

            role = await self.repo.get_role_by_name(role_name.value)
            if not role:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Role is not seeded.")

            city = None
            preferred_language = None
            if payload.city_name is not None:
                city = await self.repo.get_city_by_name(payload.city_name)
                if not city:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found.")
                if city.state and city.state.default_language:
                    preferred_language = await self.repo.get_language_by_name(city.state.default_language)

            user = await self.repo.create_user(
                name=payload.name,
                email=payload.email,
                phone=payload.phone,
                password=hash_password(payload.password),
                role_id=role.id,
                city_id=city.id if city else None,
                preferred_language_id=preferred_language.id if preferred_language else None,
                is_active=True,
                is_super_admin=False,
            )

            if role_name == RoleName.PANDIT:
                await self.repo.create_pandit_profile(
                    user_id=user.id,
                    experience_years=0,
                    description=None,
                    status=PanditProfileStatus.PENDING,
                    is_active=True,
                )

                await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            error_message = str(exc.orig).lower()
            if "users_phone_key" in error_message or "key (phone)" in error_message:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number is already registered.") from exc
            if "users_email_key" in error_message or "key (email)" in error_message:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.") from exc
            raise

        saved_user = await self.repo.get_user_by_id(user.id)
        return self.serialize_user(saved_user)

    async def login(self, *, email: str, password: str) -> TokenResponse:
        """Authenticate a user and return an access token payload."""
        user = await self.repo.get_user_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive. Please contact support.")

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.role_name,
            email=user.email,
        )
        message, can_access_pandit_features = self._build_login_message(user)
        return TokenResponse(
            access_token=access_token,
            message=message,
            user=self.serialize_user(user),
            can_access_pandit_features=can_access_pandit_features,
        )

    async def forgot_password(self, payload: ForgotPasswordRequest) -> tuple[str, str]:
        """Generate and persist a password reset token for the user."""
        user = await self.repo.get_user_by_email(payload.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        reset_token, expires_at = create_password_reset_token(user.email)
        user.forgot_password_token = hash_password_reset_token(reset_token)
        user.token_expiry = expires_at
        await self.db.commit()

        return user.email, reset_token

    async def reset_password(self, payload: ResetPasswordRequest) -> None:
        """Reset a user's password after validating the reset token."""
        if payload.new_password != payload.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password do not match.",
            )

        token_payload = verify_password_reset_token(payload.token)
        if not token_payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token.")

        user = await self.repo.get_user_by_reset_token(
            token_payload.get("sub"),
            hash_password_reset_token(payload.token),
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token.")

        now = datetime.now(timezone.utc)
        if not user.token_expiry or user.token_expiry < now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired.")

        user.password = hash_password(payload.new_password)
        user.forgot_password_token = None
        user.token_expiry = None
        await self.db.commit()

    def _build_login_message(self, user) -> tuple[str, bool]:
        """Summarize the pandit account state for the login response."""
        if user.role.role_name != RoleName.PANDIT.value:
            return "Login successful.", False

        pandit_profile = user.pandit_profile
        if not pandit_profile:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pandit profile is missing.")

        if not pandit_profile.is_active:
            return "Pandit account is deactivated. Pandit business features are blocked until reactivated by admin.", False

        if pandit_profile.status == PanditProfileStatus.PENDING:
            return "Pandit account is pending admin approval. You are logged in, but pandit features are restricted.", False

        if pandit_profile.status == PanditProfileStatus.REJECTED:
            return "Pandit account has been rejected by admin. Pandit features remain blocked.", False

        return "Login successful.", True

    @staticmethod
    def serialize_user(user) -> UserResponse:
        """Convert a loaded user model into the auth response schema."""
        pandit_profile = user.pandit_profile
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role.role_name,
            is_active=user.is_active,
            is_super_admin=user.is_super_admin,
            city_name=user.city.city_name if user.city else None,
            pandit_status=pandit_profile.status.value if pandit_profile else None,
            pandit_profile_active=pandit_profile.is_active if pandit_profile else None,
        )
