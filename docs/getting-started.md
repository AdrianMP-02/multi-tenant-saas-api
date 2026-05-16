# Getting Started

## Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development without Docker)

## Quick Start (Docker)

```bash
# Clone and start
docker compose up -d --build

# Verify it's running
curl http://localhost:8000/health

# Open interactive docs (development only)
# http://localhost:8000/docs
```

The API is available at `http://localhost:8000`. Three containers are created:

| Container | Purpose |
|---|---|
| `saas-api` | FastAPI application |
| `saas-db` | PostgreSQL 16 |
| `saas-redis` | Redis 7 (for future session/buffer needs) |

## Local Development (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -e ".[dev]"

# Ensure PostgreSQL is running locally with:
#   Database: saas_db
#   User: saas_user
#   Password: saas_pass

# Start the server
uvicorn app.main:app --reload
```

## Default Admin

On first startup, the system creates a default superadmin account:

| Field | Value |
|---|---|
| Email | `admin@saas.example` |
| Password | `admin123` |

**Change these in production** via the `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD` environment variables.

## Verify the Setup

```bash
# Health check
curl http://localhost:8000/health
# {"status":"ok","environment":"development"}

# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyPass123!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyPass123!"}'
```
