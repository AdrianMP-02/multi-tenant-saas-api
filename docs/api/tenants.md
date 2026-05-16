# Tenants API

Base path: `/api/v1/tenants`

All tenant endpoints require authentication via Bearer token.

## Tenant Statuses

| Status | Description |
|---|---|
| `trial` | New tenant, trial period |
| `active` | Active subscription |
| `inactive` | No active subscription |
| `suspended` | Suspended due to payment or policy violation |

## POST /

Create a new tenant. The creating user is automatically added as an `owner`.

### Request

```
POST /api/v1/tenants/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "subdomain": "acme"
}
```

| Field | Type | Constraints |
|---|---|---|
| `name` | string | 1–255 characters |
| `slug` | string | 2–100 chars, pattern `^[a-z0-9-]+$` |
| `subdomain` | string (optional) | Max 100 characters |

### Response 201

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "subdomain": "acme",
  "schema_name": "tenant_acme_corp",
  "status": "trial",
  "settings": null,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Errors

| Status | Description |
|---|---|
| `409 Conflict` | `Tenant with this slug already exists` |

**Note:** Creating a tenant also provisions a new PostgreSQL schema and creates all required tables.

---

## GET /

List all tenants the current user is a member of.

### Request

```
GET /api/v1/tenants/
Authorization: Bearer <access_token>
```

### Response 200

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Acme Corp",
    "slug": "acme-corp",
    "subdomain": "acme",
    "schema_name": "tenant_acme_corp",
    "status": "trial",
    "settings": null,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

---

## GET /{tenant_id}

Get a single tenant by ID.

### Request

```
GET /api/v1/tenants/{tenant_id}
Authorization: Bearer <access_token>
X-Tenant-Id: {tenant_id}      (optional, for context)
```

### Response 200

Full tenant object (same shape as list response).

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |
| `404 Not Found` | `Tenant not found` |

---

## PUT /{tenant_id}

Update a tenant's name and/or settings.

### Request

```
PUT /api/v1/tenants/{tenant_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Acme Corp Updated",
  "settings": {
    "theme": "dark",
    "timezone": "America/New_York"
  }
}
```

| Field | Type | Constraints |
|---|---|---|
| `name` | string (optional) | Max 255 characters |
| `settings` | object (optional) | Arbitrary JSON object |

### Response 200

Updated tenant object.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |
| `404 Not Found` | `Tenant not found` |

---

## DELETE /{tenant_id}

Delete a tenant and all associated data. This is a **permanent** operation that:
- Drops the tenant's PostgreSQL schema (CASCADE — removes all tables)
- Deletes the tenant record
- Cascades to delete users, subscriptions, feature flags, and audit logs

### Request

```
DELETE /api/v1/tenants/{tenant_id}
Authorization: Bearer <access_token>
```

### Response 204

No content.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |
| `404 Not Found` | `Tenant not found` |

---

## Schema

### TenantCreateRequest

```python
class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    subdomain: str | None = Field(default=None, max_length=100)
```

### TenantUpdateRequest

```python
class TenantUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    settings: dict | None = None
```

### TenantResponse

```python
class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    subdomain: str | None
    schema_name: str
    status: TenantStatus
    settings: dict | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True
```
