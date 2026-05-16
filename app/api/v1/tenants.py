from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthUser, get_current_user, get_db, verify_tenant_membership
from app.core.exceptions import ConflictError, NotFoundError
from app.crud.tenant import create_tenant, delete_tenant, get_tenant, get_tenants, update_tenant
from app.crud.user import create_tenant_user
from app.models.user import UserRole
from app.schemas.tenant import TenantCreateRequest, TenantResponse, TenantUpdateRequest

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    return await get_tenants(db)


@router.post("/", response_model=TenantResponse, status_code=201)
async def create_tenant_endpoint(
    body: TenantCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    existing = await get_tenant(db, slug=body.slug)
    if existing:
        raise ConflictError("Tenant with this slug already exists")

    tenant = await create_tenant(db, name=body.name, slug=body.slug, subdomain=body.subdomain)

    await create_tenant_user(
        db,
        tenant_id=tenant.id,
        user_id=current_user.id,
        role=UserRole.OWNER,
    )

    return tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant_endpoint(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
    _membership=Depends(verify_tenant_membership),
):
    tenant = await get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise NotFoundError("Tenant not found")
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant_endpoint(
    tenant_id: uuid.UUID,
    body: TenantUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
    _membership=Depends(verify_tenant_membership),
):
    tenant = await update_tenant(db, tenant_id=tenant_id, **body.model_dump(exclude_none=True))
    if not tenant:
        raise NotFoundError("Tenant not found")
    return tenant


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant_endpoint(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
    _membership=Depends(verify_tenant_membership),
):
    success = await delete_tenant(db, tenant_id=tenant_id)
    if not success:
        raise NotFoundError("Tenant not found")
