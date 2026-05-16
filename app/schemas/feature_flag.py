from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FeatureFlagCreateRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9_.-]+$")
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_enabled_default: bool = False


class FeatureFlagUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    is_enabled_default: bool | None = None


class FeatureFlagResponse(BaseModel):
    id: UUID
    key: str
    name: str
    description: str | None
    is_enabled_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantFeatureFlagOverrideRequest(BaseModel):
    is_enabled: bool


class TenantFeatureFlagResponse(BaseModel):
    id: UUID
    flag_key: str
    flag_name: str
    is_enabled: bool
    is_overridden: bool

    class Config:
        from_attributes = True
