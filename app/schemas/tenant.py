from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.tenant import TenantStatus


class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    subdomain: str | None = Field(default=None, max_length=100)


class TenantUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    settings: dict | None = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    subdomain: str | None
    schema_name: str
    status: TenantStatus
    settings: dict | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True
