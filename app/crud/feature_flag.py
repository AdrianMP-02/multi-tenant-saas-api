from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature_flag import FeatureFlag, TenantFeatureFlag


async def get_feature_flags(db: AsyncSession) -> Sequence[FeatureFlag]:
    result = await db.execute(select(FeatureFlag).order_by(FeatureFlag.key))
    return result.scalars().all()


async def get_feature_flag(
    db: AsyncSession,
    flag_id: uuid.UUID | None = None,
    key: str | None = None,
) -> FeatureFlag | None:
    if flag_id:
        result = await db.execute(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    elif key:
        result = await db.execute(select(FeatureFlag).where(FeatureFlag.key == key))
    else:
        return None
    return result.scalar_one_or_none()


async def create_feature_flag(db: AsyncSession, **kwargs) -> FeatureFlag:
    flag = FeatureFlag(**kwargs)
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return flag


async def update_feature_flag(
    db: AsyncSession,
    flag_id: uuid.UUID,
    **kwargs,
) -> FeatureFlag | None:
    flag = await get_feature_flag(db, flag_id=flag_id)
    if not flag:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(flag, key):
            setattr(flag, key, value)

    await db.commit()
    await db.refresh(flag)
    return flag


async def get_tenant_flags(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(FeatureFlag).order_by(FeatureFlag.key)
    )
    all_flags = result.scalars().all()

    override_result = await db.execute(
        select(TenantFeatureFlag).where(TenantFeatureFlag.tenant_id == tenant_id)
    )
    overrides = {tff.feature_flag_id: tff for tff in override_result.scalars().all()}

    return [
        {
            "id": overrides[flag.id].id if flag.id in overrides else None,
            "flag_key": flag.key,
            "flag_name": flag.name,
            "is_enabled": (
                overrides[flag.id].is_enabled
                if flag.id in overrides
                else flag.is_enabled_default
            ),
            "is_overridden": flag.id in overrides,
        }
        for flag in all_flags
    ]


async def set_tenant_flag_override(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    flag_key: str,
    is_enabled: bool,
) -> dict | None:
    flag = await get_feature_flag(db, key=flag_key)
    if not flag:
        return None

    result = await db.execute(
        select(TenantFeatureFlag).where(
            TenantFeatureFlag.tenant_id == tenant_id,
            TenantFeatureFlag.feature_flag_id == flag.id,
        )
    )
    override = result.scalar_one_or_none()

    if override:
        override.is_enabled = is_enabled
    else:
        override = TenantFeatureFlag(
            tenant_id=tenant_id,
            feature_flag_id=flag.id,
            is_enabled=is_enabled,
        )
        db.add(override)

    await db.commit()
    await db.refresh(override)

    return {
        "id": override.id,
        "flag_key": flag.key,
        "flag_name": flag.name,
        "is_enabled": override.is_enabled,
        "is_overridden": True,
    }


async def remove_tenant_flag_override(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    flag_key: str,
) -> bool:
    flag = await get_feature_flag(db, key=flag_key)
    if not flag:
        return False

    result = await db.execute(
        select(TenantFeatureFlag).where(
            TenantFeatureFlag.tenant_id == tenant_id,
            TenantFeatureFlag.feature_flag_id == flag.id,
        )
    )
    override = result.scalar_one_or_none()
    if not override:
        return False

    await db.delete(override)
    await db.commit()
    return True
