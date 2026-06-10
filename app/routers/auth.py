"""Authentication-related API routes."""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_auth_service, get_current_active_user
from app.core.config import settings
from app.schemas import (
    ApiResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.services import AuthService
from app.utils.email import send_reset_password_email, validate_smtp_login, validate_smtp_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    """Register a new user or pandit account."""
    user = await service.register(payload)
    return ApiResponse(message="Registration successful.", data=user)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    """Authenticate a user and issue an access token."""
    token = await service.login(email=payload.email, password=payload.password)
    return ApiResponse(message="Login successful.", data=token)


# Swagger's built-in Authorize sends OAuth2 form fields, so we keep this hidden helper route.
@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    """Compatibility login route used by Swagger's OAuth helper."""
    return await service.login(email=form_data.username, password=form_data.password)


@router.post("/forgot-password", response_model=ApiResponse[None])
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    """Generate and email a password reset link."""
    validate_smtp_settings()
    validate_smtp_login()
    email, reset_token = await service.forgot_password(payload)
    reset_link = f"{settings.APP_BASE_URL}/reset-password?token={reset_token}"
    background_tasks.add_task(send_reset_password_email, email, reset_link)
    return ApiResponse(message="Password reset link sent successfully.", data=None)


@router.post("/reset-password", response_model=ApiResponse[None])
async def reset_password(payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)):
    """Reset a password using a valid reset token."""
    await service.reset_password(payload)
    return ApiResponse(message="Password reset successfully.", data=None)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user=Depends(get_current_active_user)):
    """Return the currently authenticated user profile."""
    return ApiResponse(message="Current user fetched successfully.", data=AuthService.serialize_user(current_user))
