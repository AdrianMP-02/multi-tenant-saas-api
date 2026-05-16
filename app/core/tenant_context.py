from __future__ import annotations

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field

from app.models.tenant import Tenant

tenant_context_var: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)


@dataclass
class TenantContext:
    tenant_id: uuid.UUID
    schema_name: str
    tenant: Tenant | None = field(default=None)
    user_id: uuid.UUID | None = field(default=None)
    user_role: str | None = field(default=None)


def set_tenant_context(ctx: TenantContext | None) -> None:
    tenant_context_var.set(ctx)


def get_tenant_context() -> TenantContext | None:
    return tenant_context_var.get()


def get_current_schema() -> str:
    ctx = get_tenant_context()
    if ctx:
        return ctx.schema_name
    return "public"
