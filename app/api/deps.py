from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import NamedTuple

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_token
from app.core.tenant_context import get_current_schema, set_tenant_context
from app.database import get_db as _get_db
from app.models.user import TenantUser, User, UserRole

security = HTTPBearer(auto_error=False)


class AuthUser(NamedTuple):
    id: uuid.UUID
    payload: dict


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    schema = get_current_schema()
    async with _get_db(schema) as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthUser:
    if credentials is None:
        raise UnauthorizedError("Not authenticated")

    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise UnauthorizedError("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    return AuthUser(id=uuid.UUID(payload["sub"]), payload=payload)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthUser | None:
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        return AuthUser(id=uuid.UUID(payload["sub"]), payload=payload)
    except ValueError:
        return None


async def verify_tenant_membership(
    tenant_id: uuid.UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TenantUser | None:
    user_result = await db.execute(select(User).where(User.id == current_user.id))
    user = user_result.scalar_one_or_none()
    if user and user.is_superadmin:
        return None

    result = await db.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == current_user.id,
            TenantUser.status == "active",
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise ForbiddenError("You are not a member of this tenant")
    return membership


def require_tenant_role(allowed_roles: list[UserRole]):
    async def role_checker(
        tenant_id: uuid.UUID,
        current_user: AuthUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> TenantUser:
        membership = await verify_tenant_membership(tenant_id, current_user, db)
        if membership.role not in allowed_roles:
            raise ForbiddenError(
                f"Role {membership.role.value} not allowed. Required: {[r.value for r in allowed_roles]}"
            )
        return membership
    return role_checker


async def require_superadmin(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user or not user.is_superadmin:
        raise ForbiddenError("Superadmin privileges required")
    return user
