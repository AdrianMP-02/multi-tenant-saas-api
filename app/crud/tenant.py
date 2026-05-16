from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import create_schema
from app.models.tenant import Tenant, TenantStatus
from app.models.user import TenantUser


async def get_tenants(db: AsyncSession, user_id: uuid.UUID | None = None) -> Sequence[Tenant]:
    if user_id:
        result = await db.execute(
            select(Tenant)
            .join(TenantUser, TenantUser.tenant_id == Tenant.id)
            .where(TenantUser.user_id == user_id, TenantUser.status == "active")
            .order_by(Tenant.created_at.desc())
        )
    else:
        result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    return result.scalars().all()


async def get_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID | None = None,
    slug: str | None = None,
    subdomain: str | None = None,
) -> Tenant | None:
    if tenant_id:
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    elif slug:
        result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    elif subdomain:
        result = await db.execute(select(Tenant).where(Tenant.subdomain == subdomain))
    else:
        return None
    return result.scalar_one_or_none()


async def create_tenant(
    db: AsyncSession,
    name: str,
    slug: str,
    subdomain: str | None = None,
) -> Tenant:
    schema_name = f"tenant_{slug.replace('-', '_')}"
    tenant = Tenant(
        name=name,
        slug=slug,
        subdomain=subdomain,
        schema_name=schema_name,
        status=TenantStatus.TRIAL,
    )
    db.add(tenant)
    await db.flush()

    await create_schema(schema_name)

    await db.commit()
    await db.refresh(tenant)
    return tenant


async def update_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    **kwargs,
) -> Tenant | None:
    tenant = await get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(tenant, key):
            setattr(tenant, key, value)

    await db.commit()
    await db.refresh(tenant)
    return tenant


async def delete_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> bool:
    tenant = await get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        return False

    from app.database import drop_schema
    await drop_schema(tenant.schema_name)

    await db.delete(tenant)
    await db.commit()
    return True


async def delete_tenants(db: AsyncSession, tenant_ids: list[uuid.UUID]) -> int:
    from app.database import drop_schema

    deleted = 0
    for tid in tenant_ids:
        tenant = await get_tenant(db, tenant_id=tid)
        if tenant:
            await drop_schema(tenant.schema_name)
            await db.delete(tenant)
            deleted += 1
    await db.commit()
    return deleted
