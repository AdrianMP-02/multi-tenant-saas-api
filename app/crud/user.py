from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import TenantUser, TenantUserStatus, User, UserRole


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str, full_name: str) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_tenant_users(db: AsyncSession, tenant_id: uuid.UUID) -> Sequence:
    result = await db.execute(
        select(TenantUser, User.email, User.full_name)
        .join(User, TenantUser.user_id == User.id)
        .where(TenantUser.tenant_id == tenant_id)
        .order_by(TenantUser.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": tu.id,
            "user_id": tu.user_id,
            "email": email,
            "full_name": full_name,
            "role": tu.role,
            "status": tu.status,
            "invited_by": tu.invited_by,
            "created_at": tu.created_at,
        }
        for tu, email, full_name in rows
    ]


async def get_tenant_user(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    email: str | None = None,
) -> TenantUser | None:
    if user_id:
        result = await db.execute(
            select(TenantUser).where(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user_id,
            )
        )
    elif email:
        user = await get_user_by_email(db, email)
        if not user:
            return None
        result = await db.execute(
            select(TenantUser).where(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user.id,
            )
        )
    else:
        return None
    return result.scalar_one_or_none()


async def create_tenant_user(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    role: UserRole = UserRole.MEMBER,
) -> TenantUser:
    tenant_user = TenantUser(
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        status=TenantUserStatus.ACTIVE,
    )
    db.add(tenant_user)
    await db.commit()
    await db.refresh(tenant_user)
    return tenant_user


async def add_user_to_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    email: str,
    role: UserRole,
    invited_by: uuid.UUID | None = None,
) -> TenantUser | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None

    return await create_tenant_user(db, tenant_id=tenant_id, user_id=user.id, role=role)


async def update_tenant_user_role(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    role: UserRole,
) -> TenantUser | None:
    tenant_user = await get_tenant_user(db, tenant_id=tenant_id, user_id=user_id)
    if not tenant_user:
        return None

    tenant_user.role = role
    await db.commit()
    await db.refresh(tenant_user)
    return tenant_user


async def remove_user_from_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    tenant_user = await get_tenant_user(db, tenant_id=tenant_id, user_id=user_id)
    if not tenant_user:
        return False

    await db.delete(tenant_user)
    await db.commit()
    return True
