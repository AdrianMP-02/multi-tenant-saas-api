import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register(client: AsyncClient, sample_user_data):
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, sample_user_data):
    await client.post("/api/v1/auth/register", json=sample_user_data)
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient, sample_user_data):
    await client.post("/api/v1/auth/register", json=sample_user_data)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, sample_user_data):
    await client.post("/api/v1/auth/register", json=sample_user_data)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, sample_user_data):
    register_resp = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = register_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == sample_user_data["email"]
