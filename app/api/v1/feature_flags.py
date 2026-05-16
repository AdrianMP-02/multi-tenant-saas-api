from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_superadmin, verify_tenant_membership
from app.core.exceptions import ConflictError, NotFoundError
from app.crud.feature_flag import (
    create_feature_flag,
    get_feature_flag,
    get_feature_flags,
    get_tenant_flags,
    remove_tenant_flag_override,
    set_tenant_flag_override,
    update_feature_flag,
)
from app.schemas.feature_flag import (
    FeatureFlagCreateRequest,
    FeatureFlagResponse,
    FeatureFlagUpdateRequest,
    TenantFeatureFlagOverrideRequest,
    TenantFeatureFlagResponse,
)

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


@router.get("/", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    db: AsyncSession = Depends(get_db),
):
    return await get_feature_flags(db)


@router.post("/", response_model=FeatureFlagResponse, status_code=201)
async def create_feature_flag_endpoint(
    body: FeatureFlagCreateRequest,
    db: AsyncSession = Depends(get_db),
    _superadmin=Depends(require_superadmin),
):
    existing = await get_feature_flag(db, key=body.key)
    if existing:
        raise ConflictError("Feature flag with this key already exists")
    return await create_feature_flag(db, **body.model_dump())


@router.put("/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag_endpoint(
    flag_id: uuid.UUID,
    body: FeatureFlagUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _superadmin=Depends(require_superadmin),
):
    flag = await update_feature_flag(db, flag_id=flag_id, **body.model_dump(exclude_none=True))
    if not flag:
        raise NotFoundError("Feature flag not found")
    return flag


@router.get("/tenants/{tenant_id}", response_model=list[TenantFeatureFlagResponse])
async def list_tenant_flags(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(verify_tenant_membership),
):
    return await get_tenant_flags(db, tenant_id=tenant_id)


@router.put("/tenants/{tenant_id}/{flag_key}", response_model=TenantFeatureFlagResponse)
async def override_tenant_flag(
    tenant_id: uuid.UUID,
    flag_key: str,
    body: TenantFeatureFlagOverrideRequest,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(verify_tenant_membership),
):
    result = await set_tenant_flag_override(
        db, tenant_id=tenant_id, flag_key=flag_key, is_enabled=body.is_enabled
    )
    if not result:
        raise NotFoundError("Feature flag not found")
    return result


@router.delete("/tenants/{tenant_id}/{flag_key}", status_code=204)
async def remove_tenant_flag_override_endpoint(
    tenant_id: uuid.UUID,
    flag_key: str,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(verify_tenant_membership),
):
    success = await remove_tenant_flag_override(db, tenant_id=tenant_id, flag_key=flag_key)
    if not success:
        raise NotFoundError("Feature flag or override not found")
