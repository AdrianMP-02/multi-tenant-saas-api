# Architecture

## Schema-per-tenant Isolation

Each tenant receives a dedicated PostgreSQL schema. Data is physically isolated at the database level — queries from one tenant never accidentally read another tenant's data.

### How it works

1. **Tenant creation** (`POST /api/v1/tenants/`):
   - A new schema is created (`CreateSchema` DDL)
   - All tables are created inside that schema via `Base.metadata.create_all`
   - The tenant record is stored in the `public` schema

2. **Request routing** (`TenantMiddleware`):
   - Reads `X-Tenant-Id` or `X-Tenant-Schema` HTTP header
   - Looks up the tenant and executes `SET search_path TO <tenant_schema>, public`
   - All subsequent queries in that request are scoped to the tenant's schema

3. **Cleanup**:
   - Tenant deletion cascades: schema is dropped via `DropSchema ... CASCADE`
   - SQLAlchemy relationships on `Tenant` use `cascade="all, delete-orphan"` and `passive_deletes=True`

### Schema validation

Schema names are validated against the regex `^[a-zA-Z][a-zA-Z0-9_]{0,62}$` to prevent SQL injection. The `public` schema is always accessible.

## Authentication

JWT tokens signed with **RS256** (asymmetric RSA-2048).

| Detail | Value |
|---|---|
| Algorithm | `RS256` |
| Key size | 2048 bits |
| Signing key | RSA private key (PEM) |
| Verification key | RSA public key (PEM) |
| Access token TTL | 30 minutes (configurable) |
| Refresh token TTL | 7 days (configurable) |

### Token claims

**Access token:**
```json
{
  "sub": "<user_uuid>",
  "iat": 1700000000,
  "exp": 1700001800,
  "type": "access",
  "tenant_id": "<tenant_uuid>"  // optional, set by create_access_token
}
```

**Refresh token:**
```json
{
  "sub": "<user_uuid>",
  "iat": 1700000000,
  "exp": 1700604800,
  "type": "refresh"
}
```

### Key management

- **Development**: An ephemeral RSA-2048 key pair is generated in memory on first use. Keys are lost on restart.
- **Production**: Set `PRIVATE_KEY` and `PUBLIC_KEY` environment variables (PEM format). Generate with:

```bash
python -c "from app.config import _generate_key_pair; print(_generate_key_pair())"
```

## Authorization

Three-tier access control enforced via FastAPI dependencies:

### 1. Superadmin (`require_superadmin`)

Full system access. Required for:
- Creating/updating plans
- Creating/updating global feature flags

Stored as `is_superadmin` boolean on the `User` model.

### 2. Tenant roles (`require_tenant_role`)

Per-tenant role-based access. Four levels:

| Role | Privileges |
|---|---|
| `owner` | Full tenant control, can delete tenant |
| `admin` | Manage users, billing, feature flags |
| `member` | Access tenant resources |
| `viewer` | Read-only access |

### 3. Tenant membership (`verify_tenant_membership`)

A user must be an **active** member of a tenant to access any tenant-scoped resource. Membership is stored in the `tenant_users` join table with a `status` field (`active`, `invited`, `disabled`).

## Rate Limiting

Sliding-window in-memory rate limiter. No external dependencies.

| Endpoint | Limit | Window |
|---|---|---|
| `POST /api/v1/auth/register` | 5 requests | 60 seconds |
| `POST /api/v1/auth/login` | 10 requests | 60 seconds |

- Uses `time.monotonic()` for precision
- Thread-safe via `threading.Lock`
- **Automatically disabled in development** (`ENVIRONMENT=development`)
- On rate limit: returns `429 Too Many Requests` with `Retry-After` header

## Security Headers

Every HTTP response includes these security headers (set by `SecurityHeadersMiddleware`):

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `0` (opt-out of legacy XSS filter) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Cache-Control` | `no-store` |

## Password Hashing

Passwords are hashed with **bcrypt** (via the `bcrypt` library, not `passlib`):

```python
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
match = bcrypt.checkpw(plain.encode(), hash.encode())
```

## CORS

Configurable via `CORS_ORIGINS` environment variable (comma-separated). Default: `http://localhost:5173,http://localhost:3000`.
