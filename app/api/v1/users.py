from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    AuthUser,
    get_current_user,
    get_db,
    require_tenant_role,
    verify_tenant_membership,
)
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.crud.user import (
    add_user_to_tenant,
    get_tenant_user,
    get_tenant_users,
    remove_user_from_tenant,
    update_tenant_user_role,
)
from app.models.user import UserRole
from app.schemas.user import InviteUserRequest, TenantUserResponse, UpdateUserRoleRequest

router = APIRouter(prefix="/tenants/{tenant_id}/users", tags=["users"])


@router.get("/", response_model=list[TenantUserResponse])
async def list_users(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(verify_tenant_membership),
):
    return await get_tenant_users(db, tenant_id=tenant_id)


@router.post("/invite", response_model=TenantUserResponse, status_code=201)
async def invite_user(
    tenant_id: uuid.UUID,
    body: InviteUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
    _membership=Depends(require_tenant_role([UserRole.OWNER, UserRole.ADMIN])),
):
    existing = await get_tenant_user(db, tenant_id=tenant_id, email=body.email)
    if existing:
        raise ConflictError("User already in this tenant")

    tenant_user = await add_user_to_tenant(
        db,
        tenant_id=tenant_id,
        email=body.email,
        role=body.role,
        invited_by=current_user.id,
    )
    if not tenant_user:
        raise NotFoundError("User with this email not found")
    return tenant_user


@router.put("/{user_id}/role", response_model=TenantUserResponse)
async def update_user_role(
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    body: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_tenant_role([UserRole.OWNER, UserRole.ADMIN])),
):
    tenant_user = await update_tenant_user_role(
        db, tenant_id=tenant_id, user_id=user_id, role=body.role
    )
    if not tenant_user:
        raise NotFoundError("Tenant user not found")
    return tenant_user


@router.delete("/{user_id}", status_code=204)
async def remove_user(
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
    _membership=Depends(require_tenant_role([UserRole.OWNER, UserRole.ADMIN])),
):
    if user_id == current_user.id:
        raise ForbiddenError("Cannot remove yourself")

    success = await remove_user_from_tenant(db, tenant_id=tenant_id, user_id=user_id)
    if not success:
        raise NotFoundError("Tenant user not found")
