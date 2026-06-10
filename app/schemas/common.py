"""Shared response envelope schemas."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard wrapper used by most API endpoints."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = True
    error: Optional[object] = None
    msg: Optional[str] = Field(default=None, alias="message", serialization_alias="msg")
    data: Optional[T] = None
