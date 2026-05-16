# Testing

## Test Suite

The project uses **pytest** with **pytest-asyncio** for async database tests.

```bash
# Run all tests inside Docker
docker exec saas-api python -m pytest tests/ -v --tb=short

# Run with coverage
docker exec saas-api python -m pytest tests/ --cov=app -v

# Run a specific test file
docker exec saas-api python -m pytest tests/test_auth.py -v

# Run a specific test
docker exec saas-api python -m pytest tests/test_tenants.py::test_create_tenant -v
```

## Test Structure

```
tests/
├── conftest.py        # Fixtures: test DB, async client, auth tokens
├── test_auth.py       # Auth endpoints: register, login, refresh, me
└── test_tenants.py    # Tenant CRUD endpoints
```

### Test database

Tests use a separate database (`saas_test`) configured in `conftest.py`. Tables are created before the test session and dropped after.

**Note:** The `saas_test` database must exist in PostgreSQL. If using Docker, it's created automatically. For local dev:

```bash
createdb -U saas_user saas_test
```

## E2E Smoke Test

```bash
docker exec saas-api python -c "
import httpx

c = httpx.Client(base_url='http://localhost:8000', timeout=10)

# Health
r = c.get('/health')
assert r.status_code == 200
print('health:', r.status_code)

# Register
r = c.post('/api/v1/auth/register', json={
    'email': 'e2e@test.com',
    'password': 'Test123!',
    'full_name': 'E2E User'
})
assert r.status_code == 201
token = r.json()['access_token']
print('register:', r.status_code)

# Authenticated request
headers = {'Authorization': f'Bearer {token}'}
r = c.get('/api/v1/auth/me', headers=headers)
assert r.status_code == 200
print('me:', r.status_code, r.json()['email'])

# Create tenant (auto-assigns user as owner)
r = c.post('/api/v1/tenants/', headers=headers, json={
    'name': 'E2E Corp',
    'slug': 'e2e-corp'
})
assert r.status_code == 201
tenant_id = r.json()['id']
print('create_tenant:', r.status_code, tenant_id)

# Get tenant
r = c.get(f'/api/v1/tenants/{tenant_id}', headers=headers)
assert r.status_code == 200
print('get_tenant:', r.status_code, r.json()['name'])

# Update tenant
r = c.put(f'/api/v1/tenants/{tenant_id}', headers=headers, json={
    'name': 'E2E Corp Updated'
})
assert r.status_code == 200
print('update_tenant:', r.status_code)

# Delete tenant
r = c.delete(f'/api/v1/tenants/{tenant_id}', headers=headers)
assert r.status_code == 204
print('delete_tenant:', r.status_code)

print()
print('E2E PASSED')
"
```

## Current Coverage

- **12 tests**, all passing
- Auth: register, duplicate email, login, invalid password, refresh, get profile
- Tenants: create, list, duplicate slug, get, update, delete

## Writing Tests

### Fixtures available

| Fixture | Description |
|---|---|
| `db_session` | Creates a fresh async DB session |
| `async_client` | FastAPI TestClient for HTTP requests |
| `user_token_headers` | Registered user's auth headers |
| `test_user` | Registered user data (id, email) |

### Pattern

```python
async def test_something(async_client):
    r = await async_client.get("/api/v1/plans/")
    assert r.status_code == 200
```
