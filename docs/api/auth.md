# Authentication API

Base path: `/api/v1/auth`

## POST /register

Register a new user account. Returns JWT token pair.

**Rate limited:** 5 requests per 60 seconds (disabled in development).

### Request

```
POST /api/v1/auth/register
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "securePass123",
  "full_name": "Jane Doe"
}
```

| Field | Type | Constraints |
|---|---|---|
| `email` | string (email) | Valid email format |
| `password` | string | 8–128 characters |
| `full_name` | string | 1–255 characters |

### Response 201

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "bearer"
}
```

| Field | Type | Description |
|---|---|---|
| `access_token` | string | JWT (RS256), expires in 30 minutes |
| `refresh_token` | string | JWT (RS256), expires in 7 days |
| `token_type` | string | Always `bearer` |

### Errors

| Status | Description |
|---|---|
| `409 Conflict` | `Email already registered` |

---

## POST /login

Authenticate with email and password. Returns JWT token pair.

**Rate limited:** 10 requests per 60 seconds (disabled in development).

### Request

```
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "securePass123"
}
```

### Response 200

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "bearer"
}
```

### Errors

| Status | Description |
|---|---|
| `401 Unauthorized` | `Invalid email or password` |
| `401 Unauthorized` | `Account is disabled` |

---

## POST /refresh

Obtain a new token pair using a refresh token. No authentication required; the refresh token itself authorizes the request.

### Request

```
POST /api/v1/auth/refresh
Content-Type: application/json
```

```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

### Response 200

Same shape as login/register — new `access_token` and `refresh_token`.

### Errors

| Status | Description |
|---|---|
| `401 Unauthorized` | `Invalid or expired refresh token` |
| `401 Unauthorized` | `Invalid token type` |

---

## GET /me

Get the authenticated user's profile. Requires a valid access token.

### Request

```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Response 200

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "jane@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_superadmin": false,
  "created_at": "2025-01-01T00:00:00Z"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | UUID | User's unique identifier |
| `email` | string | User's email address |
| `full_name` | string | User's display name |
| `is_active` | boolean | Whether the account is active |
| `is_superadmin` | boolean | System-wide superadmin privileges |
| `created_at` | datetime (ISO 8601) | Account creation timestamp |

### Errors

| Status | Description |
|---|---|
| `401 Unauthorized` | `Not authenticated` — missing or malformed token |
| `401 Unauthorized` | `Invalid or expired token` |
| `404 Not Found` | `User not found` — token valid but user deleted |

---

## Schema

### RegisterRequest

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
```

### LoginRequest

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

### TokenResponse

```python
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

### RefreshRequest

```python
class RefreshRequest(BaseModel):
    refresh_token: str
```

### UserResponse

```python
class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_superadmin: bool
    created_at: datetime

    class Config:
        from_attributes = True
```
