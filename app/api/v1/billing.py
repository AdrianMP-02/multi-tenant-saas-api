from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_tenant_role, verify_tenant_membership
from app.core.exceptions import BadRequestError, NotFoundError
from app.crud.plan import get_plan
from app.crud.tenant import get_tenant
from app.models.user import UserRole

router = APIRouter(prefix="/tenants/{tenant_id}/billing", tags=["billing"])


@router.post("/subscribe")
async def subscribe(
    tenant_id: uuid.UUID,
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_tenant_role([UserRole.OWNER, UserRole.ADMIN])),
):
    tenant = await get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise NotFoundError("Tenant not found")

    plan = await get_plan(db, plan_id=plan_id)
    if not plan:
        raise NotFoundError("Plan not found")

    if not plan.is_active:
        raise BadRequestError("Plan is not active")

    return {"message": "Subscription created (Stripe integration pending)"}


@router.post("/cancel")
async def cancel_subscription(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_tenant_role([UserRole.OWNER, UserRole.ADMIN])),
):
    return {"message": "Subscription canceled (Stripe integration pending)"}


@router.get("/invoices")
async def list_invoices(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _membership=Depends(verify_tenant_membership),
):
    return []
