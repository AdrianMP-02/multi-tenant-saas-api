# Project Structure

```
multi-tenant-saas-api/
├── app/                              # Application package
│   ├── __init__.py
│   │
│   ├── api/                          # HTTP layer
│   │   ├── deps.py                   # FastAPI dependencies (auth, DB, RBAC)
│   │   └── v1/                       # API version 1
│   │       ├── router.py             # Aggregates all v1 routers
│   │       ├── auth.py               # /auth endpoints
│   │       ├── billing.py            # /billing endpoints
│   │       ├── feature_flags.py      # /feature-flags endpoints
│   │       ├── plans.py              # /plans endpoints
│   │       ├── tenants.py            # /tenants endpoints
│   │       └── users.py              # /tenants/{id}/users endpoints
│   │
│   ├── core/                         # Business logic & infrastructure
│   │   ├── exceptions.py             # HTTP exception classes
│   │   ├── rate_limiter.py           # In-memory sliding-window rate limiter
│   │   ├── security.py               # JWT (RS256) + bcrypt password hashing
│   │   └── tenant_context.py         # Request-scoped tenant context
│   │
│   ├── crud/                         # Data access layer (per-model)
│   │   ├── feature_flag.py
│   │   ├── plan.py
│   │   ├── tenant.py
│   │   └── user.py
│   │
│   ├── middleware/                   # ASGI middleware
│   │   ├── audit_middleware.py       # Audit logging for mutating requests
│   │   ├── security_headers.py       # Security response headers
│   │   └── tenant_middleware.py      # Schema-per-tenant resolution
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── audit_log.py
│   │   ├── feature_flag.py
│   │   ├── plan.py
│   │   ├── subscription.py
│   │   ├── tenant.py
│   │   └── user.py
│   │
│   ├── schemas/                      # Pydantic request/response models
│   │   ├── auth.py
│   │   ├── feature_flag.py
│   │   ├── plan.py
│   │   ├── tenant.py
│   │   └── user.py
│   │
│   ├── config.py                     # Pydantic-settings configuration
│   ├── database.py                   # Engine, session factory, schema DDL
│   └── main.py                       # FastAPI app creation & lifespan
│
├── docker/
│   └── Dockerfile                    # Multi-stage build (dev + prod)
│
├── docs/                             # Documentation
│   ├── getting-started.md
│   ├── architecture.md
│   ├── configuration.md
│   ├── testing.md
│   ├── project-structure.md
│   └── api/
│       ├── auth.md
│       ├── billing.md
│       ├── feature-flags.md
│       ├── plans.md
│       ├── tenants.md
│       └── users.md
│
├── tests/                            # Pytest test suite
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_tenants.py
│
├── .env                              # Environment variables (not committed)
├── .gitignore
├── docker-compose.yml                # Docker Compose services
├── pyproject.toml                    # Project metadata & dependencies
└── README.md                         # Project overview
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Schema-per-tenant** | Physical data isolation over row-level filtering — simpler security model, no risk of `WHERE tenant_id = ?` mistakes |
| **Pure ASGI middleware** | Avoids Starlette `BaseHTTPMiddleware` anyio task-group issues with asyncpg connections |
| **RS256 (asymmetric JWT)** | Private key stays on the auth server; public key can be distributed to microservices for stateless verification |
| **In-memory rate limiter** | Zero external dependencies; can be swapped for Redis-based if scaling horizontally |
| **NullPool in development** | Prevents asyncpg `Pool` from holding connections across event loops during test reloads |
