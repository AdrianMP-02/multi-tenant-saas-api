# Tenant Users API

Base path: `/api/v1/tenants/{tenant_id}/users`

All endpoints require authentication via Bearer token and active membership in the tenant.

## User Roles

| Role | Privileges |
|---|---|
| `owner` | Full control, can delete tenant, manage all settings |
| `admin` | Manage users, billing, feature flags |
| `member` | Access standard tenant resources |
| `viewer` | Read-only access |

## User Statuses

| Status | Description |
|---|---|
| `active` | User is an active member |
| `invited` | User has been invited but hasn't accepted |
| `disabled` | User has been removed or disabled |

## GET /

List all users in a tenant.

### Request

```
GET /api/v1/tenants/{tenant_id}/users/
Authorization: Bearer <access_token>
```

### Response 200

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "full_name": "Alice Smith",
    "role": "owner",
    "status": "active",
    "invited_by": null,
    "created_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "email": "bob@example.com",
    "full_name": "Bob Jones",
    "role": "member",
    "status": "active",
    "invited_by": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-01-02T00:00:00Z"
  }
]
```

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |

---

## POST /invite

Invite an existing registered user to the tenant.

**Authorization:** Requires `owner` or `admin` role.

### Request

```
POST /api/v1/tenants/{tenant_id}/users/invite
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "role": "member"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `email` | string (email) | — | Must match an existing registered user |
| `role` | string | `member` | One of: `owner`, `admin`, `member`, `viewer` |

### Response 201

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "email": "user@example.com",
  "full_name": "Charlie Brown",
  "role": "member",
  "status": "active",
  "invited_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-03T00:00:00Z"
}
```

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | Insufficient role — requires `owner` or `admin` |
| `404 Not Found` | `User with this email not found` (not registered) |
| `409 Conflict` | `User already in this tenant` |

---

## PUT /{user_id}/role

Update a user's role within the tenant.

**Authorization:** Requires `owner` or `admin` role.

### Request

```
PUT /api/v1/tenants/{tenant_id}/users/{user_id}/role
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "role": "admin"
}
```

### Response 200

Updated tenant user object (same shape as list response).

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | Insufficient role |
| `404 Not Found` | `Tenant user not found` |

---

## DELETE /{user_id}

Remove a user from the tenant.

**Authorization:** Requires `owner` or `admin` role.

### Request

```
DELETE /api/v1/tenants/{tenant_id}/users/{user_id}
Authorization: Bearer <access_token>
```

### Response 204

No content.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `Cannot remove yourself` or insufficient role |
| `404 Not Found` | `Tenant user not found` |

---

## Schema

### InviteUserRequest

```python
class InviteUserRequest(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER
```

### UpdateUserRoleRequest

```python
class UpdateUserRoleRequest(BaseModel):
    role: UserRole
```

### TenantUserResponse

```python
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
```
