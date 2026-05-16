# Feature Flags API

Base path: `/api/v1/feature-flags`

Feature flags provide a way to toggle functionality globally and per-tenant. Global flags define a default value; tenants can override individual flags.

## Global feature flags

Global flags are managed by superadmins. The default value applies to all tenants unless overridden.

## Per-tenant overrides

Tenant members with sufficient role can override a global flag for their specific tenant. Overrides can be removed to revert to the global default.

## GET /

List all global feature flags. Public endpoint.

### Request

```
GET /api/v1/feature-flags/
```

### Response 200

```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "key": "dark_mode",
    "name": "Dark Mode",
    "description": "Enable dark mode UI",
    "is_enabled_default": false,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440004",
    "key": "new_onboarding",
    "name": "New Onboarding Flow",
    "description": "Use the redesigned onboarding wizard",
    "is_enabled_default": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

---

## POST /

Create a global feature flag.

**Authorization:** Superadmin only.

### Request

```
POST /api/v1/feature-flags/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "key": "dark_mode",
  "name": "Dark Mode",
  "description": "Enable dark mode UI",
  "is_enabled_default": false
}
```

| Field | Type | Default | Constraints |
|---|---|---|---|
| `key` | string | — | 1–100 chars, pattern `^[a-z0-9_.-]+$` |
| `name` | string | — | 1–255 characters |
| `description` | string (optional) | — | — |
| `is_enabled_default` | bool | `false` | Global default value |

### Response 201

Full feature flag object.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `Superadmin privileges required` |
| `409 Conflict` | `Feature flag with this key already exists` |

---

## PUT /{flag_id}

Update a global feature flag.

**Authorization:** Superadmin only.

### Request

```
PUT /api/v1/feature-flags/{flag_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Dark Mode v2",
  "is_enabled_default": true
}
```

All fields optional.

### Response 200

Updated feature flag object.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `Superadmin privileges required` |
| `404 Not Found` | `Feature flag not found` |

---

## GET /tenants/{tenant_id}

Get effective feature flags for a tenant. Merges global defaults with tenant overrides.

**Authorization:** Bearer token. User must be an active member of the tenant.

### Request

```
GET /api/v1/feature-flags/tenants/{tenant_id}
Authorization: Bearer <access_token>
X-Tenant-Id: {tenant_id}
```

### Response 200

```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "flag_key": "dark_mode",
    "flag_name": "Dark Mode",
    "is_enabled": true,
    "is_overridden": true
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440004",
    "flag_key": "new_onboarding",
    "flag_name": "New Onboarding Flow",
    "is_enabled": true,
    "is_overridden": false
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Feature flag ID |
| `flag_key` | string | Unique key identifier |
| `flag_name` | string | Human-readable name |
| `is_enabled` | bool | Effective value (override or global default) |
| `is_overridden` | bool | Whether tenant has a custom override |

---

## PUT /tenants/{tenant_id}/{flag_key}

Set a tenant-level override for a feature flag.

**Authorization:** Bearer token. User must be an active member.

### Request

```
PUT /api/v1/feature-flags/tenants/{tenant_id}/{flag_key}
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "is_enabled": true
}
```

### Response 200

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "flag_key": "dark_mode",
  "flag_name": "Dark Mode",
  "is_enabled": true,
  "is_overridden": true
}
```

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |
| `404 Not Found` | `Feature flag not found` — invalid flag_key |

---

## DELETE /tenants/{tenant_id}/{flag_key}

Remove a tenant-level override. The flag reverts to its global default value.

**Authorization:** Bearer token. User must be an active member.

### Request

```
DELETE /api/v1/feature-flags/tenants/{tenant_id}/{flag_key}
Authorization: Bearer <access_token>
```

### Response 204

No content.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |
| `404 Not Found` | `Feature flag or override not found` |

---

## Schema

### FeatureFlagCreateRequest

```python
class FeatureFlagCreateRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9_.-]+$")
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_enabled_default: bool = False
```

### FeatureFlagUpdateRequest

```python
class FeatureFlagUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    is_enabled_default: bool | None = None
```

### FeatureFlagResponse

```python
class FeatureFlagResponse(BaseModel):
    id: UUID
    key: str
    name: str
    description: str | None
    is_enabled_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### TenantFeatureFlagOverrideRequest

```python
class TenantFeatureFlagOverrideRequest(BaseModel):
    is_enabled: bool
```

### TenantFeatureFlagResponse

```python
class TenantFeatureFlagResponse(BaseModel):
    id: UUID
    flag_key: str
    flag_name: str
    is_enabled: bool
    is_overridden: bool

    class Config:
        from_attributes = True
```
