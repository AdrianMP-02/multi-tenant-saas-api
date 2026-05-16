from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_superadmin
from app.core.exceptions import ConflictError, NotFoundError
from app.crud.plan import create_plan, get_plan, get_plans, update_plan
from app.schemas.plan import PlanCreateRequest, PlanResponse, PlanUpdateRequest

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/", response_model=list[PlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
):
    return await get_plans(db)


@router.post("/", response_model=PlanResponse, status_code=201)
async def create_plan_endpoint(
    body: PlanCreateRequest,
    db: AsyncSession = Depends(get_db),
    _superadmin=Depends(require_superadmin),
):
    existing = await get_plan(db, slug=body.slug)
    if existing:
        raise ConflictError("Plan with this slug already exists")
    return await create_plan(db, **body.model_dump())


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan_endpoint(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    plan = await get_plan(db, plan_id=plan_id)
    if not plan:
        raise NotFoundError("Plan not found")
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan_endpoint(
    plan_id: uuid.UUID,
    body: PlanUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _superadmin=Depends(require_superadmin),
):
    plan = await update_plan(db, plan_id=plan_id, **body.model_dump(exclude_none=True))
    if not plan:
        raise NotFoundError("Plan not found")
    return plan
