"""Authentication and authorization dependencies used by FastAPI routes."""

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.database import get_db
from app.models.enums import RoleName
from app.repositories import AuthRepository
from app.services import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_auth_service(db=Depends(get_db)) -> AuthService:
    """Build the auth service with a request-scoped repository."""
    return AuthService(AuthRepository(db))


async def get_current_user(token: str = Depends(oauth2_scheme), service: AuthService = Depends(get_auth_service)):
    """Resolve the authenticated user from the bearer access token."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise credentials_error
        user_id = payload.get("user_id")
        if not user_id:
            raise credentials_error
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    user = await service.repo.get_user_by_id(UUID(user_id))
    if not user:
        raise credentials_error
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Ensure the authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account.")
    return current_user


async def get_current_admin(current_user=Depends(get_current_active_user)):
    """Ensure the authenticated user has admin privileges."""
    if current_user.role.role_name != RoleName.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user
