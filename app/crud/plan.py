from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


async def get_plans(db: AsyncSession) -> Sequence[Plan]:
    result = await db.execute(select(Plan).order_by(Plan.price_cents))
    return result.scalars().all()


async def get_plan(
    db: AsyncSession,
    plan_id: uuid.UUID | None = None,
    slug: str | None = None,
) -> Plan | None:
    if plan_id:
        result = await db.execute(select(Plan).where(Plan.id == plan_id))
    elif slug:
        result = await db.execute(select(Plan).where(Plan.slug == slug))
    else:
        return None
    return result.scalar_one_or_none()


async def create_plan(db: AsyncSession, **kwargs) -> Plan:
    plan = Plan(**kwargs)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def update_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
    **kwargs,
) -> Plan | None:
    plan = await get_plan(db, plan_id=plan_id)
    if not plan:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(plan, key):
            setattr(plan, key, value)

    await db.commit()
    await db.refresh(plan)
    return plan
