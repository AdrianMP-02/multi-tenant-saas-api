# Plans API

Base path: `/api/v1/plans`

Plans define subscription tiers (pricing, features, limits). List and get endpoints are public; create and update require superadmin privileges.

## GET /

List all subscription plans.

### Request

```
GET /api/v1/plans/
```

### Response 200

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Starter",
    "slug": "starter",
    "description": "For small teams",
    "price_cents": 0,
    "currency": "usd",
    "features": {},
    "max_users": 5,
    "max_storage_mb": 100,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "name": "Pro",
    "slug": "pro",
    "description": "For growing businesses",
    "price_cents": 2900,
    "currency": "usd",
    "features": {
      "advanced_reports": true,
      "api_access": true
    },
    "max_users": 25,
    "max_storage_mb": 1024,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

---

## POST /

Create a new plan.

**Authorization:** Superadmin only.

### Request

```
POST /api/v1/plans/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Enterprise",
  "slug": "enterprise",
  "description": "For large organizations",
  "price_cents": 9900,
  "currency": "usd",
  "features": {
    "sso": true,
    "audit_logs": true,
    "custom_branding": true
  },
  "max_users": 100,
  "max_storage_mb": 10240,
  "is_active": true
}
```

| Field | Type | Default | Constraints |
|---|---|---|---|
| `name` | string | — | 1–255 characters |
| `slug` | string | — | 2–100 chars, pattern `^[a-z0-9-]+$` |
| `description` | string (optional) | — | — |
| `price_cents` | int | — | >= 0 |
| `currency` | string | `usd` | — |
| `features` | object | `{}` | Arbitrary JSON (plan capabilities) |
| `max_users` | int | `1` | >= 1 |
| `max_storage_mb` | int | `100` | >= 0 |
| `is_active` | bool | `true` | Inactive plans cannot be subscribed to |

### Response 201

Full plan object (same shape as list response).

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `Superadmin privileges required` |
| `409 Conflict` | `Plan with this slug already exists` |

---

## GET /{plan_id}

Get a single plan by ID.

### Request

```
GET /api/v1/plans/{plan_id}
```

### Response 200

Full plan object.

### Errors

| Status | Description |
|---|---|
| `404 Not Found` | `Plan not found` |

---

## PUT /{plan_id}

Update a plan.

**Authorization:** Superadmin only.

### Request

```
PUT /api/v1/plans/{plan_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "price_cents": 7900,
  "max_users": 200,
  "is_active": false
}
```

All fields are optional. Only provided fields are updated.

### Response 200

Updated plan object.

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `Superadmin privileges required` |
| `404 Not Found` | `Plan not found` |

---

## Schema

### PlanCreateRequest

```python
class PlanCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    price_cents: int = Field(ge=0)
    currency: str = "usd"
    features: dict = Field(default_factory=dict)
    max_users: int = Field(ge=1, default=1)
    max_storage_mb: int = Field(ge=0, default=100)
    is_active: bool = True
```

### PlanUpdateRequest

```python
class PlanUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    currency: str | None = None
    features: dict | None = None
    max_users: int | None = Field(default=None, ge=1)
    max_storage_mb: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
```

### PlanResponse

```python
class PlanResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    price_cents: int
    currency: str
    features: dict
    max_users: int
    max_storage_mb: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```
