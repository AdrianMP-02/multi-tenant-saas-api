from __future__ import annotations

import uuid

from sqlalchemy import select, text
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.tenant_context import TenantContext, set_tenant_context
from app.database import session_factory, validate_schema_name
from app.models.tenant import Tenant


class TenantMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        tenant_id_header = headers.get("x-tenant-id")
        tenant_schema = headers.get("x-tenant-schema")

        if tenant_id_header or tenant_schema:
            async with session_factory() as session:
                try:
                    if tenant_id_header:
                        result = await session.execute(
                            select(Tenant).where(Tenant.id == uuid.UUID(tenant_id_header))
                        )
                    else:
                        validate_schema_name(tenant_schema)
                        result = await session.execute(
                            select(Tenant).where(Tenant.schema_name == tenant_schema)
                        )
                except (ValueError, TypeError):
                    result = None

                tenant = result.scalar_one_or_none() if result is not None else None

                if tenant:
                    ctx = TenantContext(
                        tenant_id=tenant.id,
                        schema_name=tenant.schema_name,
                        tenant=tenant,
                    )
                    set_tenant_context(ctx)

                    quoted = (
                        session.bind.dialect.identifier_preparer.quote_schema(tenant.schema_name)
                        if session.bind
                        else tenant.schema_name
                    )
                    async with session.begin():
                        await session.execute(
                            text(f"SET search_path TO {quoted}, public")
                        )

        try:
            await self.app(scope, receive, send)
        finally:
            set_tenant_context(None)
