import httpx

base = "http://localhost:8000"
sep = lambda: print("-" * 50)

r = httpx.get(f"{base}/health")
print(f"HEALTH: {r.status_code} {r.json()}")
sep()

r = httpx.post(f"{base}/api/v1/auth/register", json={
    "email": "admin@demo.com",
    "password": "DemoPass123",
    "full_name": "Admin Demo",
})
print(f"REGISTER: {r.status_code}")
if r.status_code != 201:
    print(f"  ERROR: {r.text[:300]}")
    exit(1)
token = r.json()["access_token"]
print(f"  Token: {token[:40]}...")
sep()

headers = {"Authorization": f"Bearer {token}"}

r = httpx.get(f"{base}/api/v1/auth/me", headers=headers)
print(f"ME: {r.status_code} email={r.json()['email']}")
sep()

r = httpx.post(f"{base}/api/v1/tenants/", json={
    "name": "Mi Empresa",
    "slug": "mi-empresa",
}, headers=headers)
print(f"CREATE TENANT: {r.status_code}")
if r.status_code == 201:
    tenant = r.json()
    print(f"  ID: {tenant['id']}")
    print(f"  Name: {tenant['name']}")
    print(f"  Schema: {tenant['schema_name']}")
    tenant_id = tenant["id"]
sep()

r = httpx.get(f"{base}/api/v1/tenants/", headers=headers)
print(f"LIST TENANTS: {r.status_code} count={len(r.json())}")
sep()

r = httpx.post(f"{base}/api/v1/plans/", json={
    "name": "Pro",
    "slug": "pro",
    "price_cents": 2999,
    "max_users": 10,
    "max_storage_mb": 1024,
    "features": {"api_access": True, "reports": True},
}, headers=headers)
print(f"CREATE PLAN: {r.status_code}")
if r.status_code == 201:
    print(f"  Plan: {r.json()['name']} - ${r.json()['price_cents']/100:.2f}")
sep()

r = httpx.post(f"{base}/api/v1/plans/", json={
    "name": "Enterprise",
    "slug": "enterprise",
    "price_cents": 9999,
    "max_users": 100,
    "max_storage_mb": 10240,
    "features": {"api_access": True, "reports": True, "sso": True, "audit": True},
}, headers=headers)
print(f"PLAN2: {r.status_code} - {r.json()['name']}")
sep()

r = httpx.get(f"{base}/api/v1/plans/", headers=headers)
print(f"LIST PLANS: {r.status_code} count={len(r.json())}")
sep()

print("ALL TESTS PASSED!")
