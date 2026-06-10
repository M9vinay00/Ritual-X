"""Password hashing and token helpers used by auth flows."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    """Hash a password with a per-password random salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the stored salted hash."""
    try:
        salt, password_hash = hashed_password.split("$", 1)
    except ValueError:
        return False

    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return secrets.compare_digest(candidate_hash, password_hash)


def create_access_token(*, user_id: str, role: str, email: str) -> str:
    """Create a signed JWT access token for the authenticated user."""
    expires_at = utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "role": role,
        "email": email,
        "type": "access",
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def create_password_reset_token(email: str) -> tuple[str, datetime]:
    """Create a short-lived token dedicated to password reset flows."""
    expires_at = utcnow() + timedelta(minutes=settings.FORGOT_PASSWORD_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "purpose": "forgot-password",
        "nonce": secrets.token_urlsafe(24),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def verify_password_reset_token(reset_token: str) -> dict | None:
    """Validate a password reset token and enforce its intended purpose."""
    try:
        payload = jwt.decode(reset_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("purpose") != "forgot-password":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def hash_password_reset_token(reset_token: str) -> str:
    """Hash reset tokens before persisting them to the database."""
    return hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
