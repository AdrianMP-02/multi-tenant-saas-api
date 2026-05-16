import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient, sample_user_data, sample_tenant_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_tenant_data["name"]
    assert data["slug"] == sample_tenant_data["slug"]


@pytest.mark.asyncio
async def test_list_tenants(client: AsyncClient, sample_user_data, sample_tenant_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)

    response = await client.get("/api/v1/tenants/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_duplicate_tenant(client: AsyncClient, sample_user_data, sample_tenant_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)
    response = await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_tenant(client: AsyncClient, sample_user_data, sample_tenant_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)
    tenant_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/tenants/{tenant_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == tenant_id


@pytest.mark.asyncio
async def test_update_tenant(client: AsyncClient, sample_user_data, sample_tenant_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)
    tenant_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/tenants/{tenant_id}",
        json={"name": "Updated Name"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_tenant(client: AsyncClient, sample_user_data, sample_tenant_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/tenants/", json=sample_tenant_data, headers=headers)
    tenant_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/tenants/{tenant_id}", headers=headers)
    assert response.status_code == 204
