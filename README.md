# Multi-tenant SaaS API

**Version:** 0.1.0 | **Stack:** FastAPI + PostgreSQL + Redis

Multi-tenant SaaS backend with schema-per-tenant isolation, JWT authentication (RS256), role-based access control, rate limiting, and Stripe billing integration.

```bash
docker compose up -d --build
```

Open `http://localhost:8000/docs` (development only).

---

## Documentation

| Section | File |
|---|---|
| Quick Start | [docs/getting-started.md](docs/getting-started.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Configuration | [docs/configuration.md](docs/configuration.md) |
| API Reference | [docs/api/auth.md](docs/api/auth.md) · [tenants](docs/api/tenants.md) · [users](docs/api/users.md) · [plans](docs/api/plans.md) · [feature-flags](docs/api/feature-flags.md) · [billing](docs/api/billing.md) |
| Testing | [docs/testing.md](docs/testing.md) |
| Project Structure | [docs/project-structure.md](docs/project-structure.md) |
