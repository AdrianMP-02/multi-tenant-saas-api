# Configuration

All configuration is managed via environment variables (loaded from `.env` by `pydantic-settings`).

## Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://saas_user:saas_pass@localhost:5432/saas_db` | PostgreSQL connection string |

In Docker, `db` is used as the hostname (overridden in `docker-compose.yml`):
```
DATABASE_URL=postgresql+asyncpg://saas_user:saas_pass@db:5432/saas_db
```

## JWT / Security

| Variable | Default | Description |
|---|---|---|
| `PRIVATE_KEY` | — | RSA private key in PEM format. Auto-generated in development. **Required in production.** |
| `PUBLIC_KEY` | — | RSA public key in PEM format. Auto-generated in development. **Required in production.** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime |

## Redis (optional)

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | — | Redis connection string (e.g. `redis://localhost:6379/0`) |

## Stripe (optional)

| Variable | Default | Description |
|---|---|---|
| `STRIPE_SECRET_KEY` | — | Stripe API secret key |
| `STRIPE_WEBHOOK_SECRET` | — | Stripe webhook signing secret |

Currently used for plan management; actual payment processing is marked as pending.

## App

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` or `production`. Controls debug mode, rate limiting, auto-generated RSA keys, OpenAPI docs visibility |
| `DEBUG` | `true` | Enables SQLAlchemy echo and other debug behavior |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated allowed CORS origins |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server listen port |

## Default Admin

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_ADMIN_EMAIL` | `admin@saas.local` | Email for the auto-created superadmin user |
| `DEFAULT_ADMIN_PASSWORD` | `admin123` | Password for the auto-created superadmin user |

## Environment-specific behavior

### Development (`ENVIRONMENT=development`)
- RSA key pair auto-generated in memory
- Rate limiter disabled
- OpenAPI docs available at `/docs`
- SQLAlchemy `NullPool` (no connection pooling — avoids asyncpg event-loop issues)
- SQL echo enabled when `DEBUG=true`

### Production (`ENVIRONMENT=production`)
- `PRIVATE_KEY` and `PUBLIC_KEY` must be set explicitly
- Rate limiter active on auth endpoints
- OpenAPI docs disabled
- SQLAlchemy connection pooling (`pool_size=5`, `max_overflow=10`)
- If `SECRET_KEY`-like defaults are detected, raises `RuntimeError`
