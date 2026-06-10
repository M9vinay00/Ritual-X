import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    role: Literal["user", "pandit"]
    city_name: Optional[str] = Field(default=None, min_length=2, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    role: str
    is_active: bool
    is_super_admin: bool
    city_name: Optional[str] = None
    pandit_status: Optional[str] = None
    pandit_profile_active: Optional[bool] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str
    user: UserResponse
    can_access_pandit_features: bool = False
