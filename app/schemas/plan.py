from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlanCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    price_cents: int = Field(ge=0)
    currency: str = "usd"
    features: dict = Field(default_factory=dict)
    max_users: int = Field(ge=1, default=1)
    max_storage_mb: int = Field(ge=0, default=100)
    is_active: bool = True


class PlanUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    currency: str | None = None
    features: dict | None = None
    max_users: int | None = Field(default=None, ge=1)
    max_storage_mb: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class PlanResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    price_cents: int
    currency: str
    features: dict
    max_users: int
    max_storage_mb: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
