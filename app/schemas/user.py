from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import TenantUserStatus, UserRole


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER


class UpdateUserRoleRequest(BaseModel):
    role: UserRole


class TenantUserResponse(BaseModel):
    id: UUID
    user_id: UUID
    email: str
    full_name: str
    role: UserRole
    status: TenantUserStatus
    invited_by: UUID | None
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
