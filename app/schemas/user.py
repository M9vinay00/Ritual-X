from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    is_super_admin: bool
    city_name: Optional[str] = None
    preferred_language_name: Optional[str] = None
    pandit_status: Optional[str] = None
    pandit_profile_active: Optional[bool] = None


class UpdateMeRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    city_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    preferred_language_name: Optional[str] = Field(default=None, min_length=2, max_length=100)


class ChangeLanguageRequest(BaseModel):
    preferred_language_name: str = Field(min_length=2, max_length=100)
