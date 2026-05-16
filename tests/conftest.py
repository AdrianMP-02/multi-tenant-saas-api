from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://saas_user:saas_pass@db:5432/saas_test"


def pytest_collection_modifyitems(items):
    for item in items:
        marker = item.get_closest_marker("asyncio")
        if marker is not None:
            item.keywords["asyncio"] = pytest.mark.asyncio(loop_scope="session", **marker.kwargs)


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_user_data() -> dict:
    return {
        "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_tenant_data() -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"Test Tenant {suffix}",
        "slug": f"test-tenant-{suffix}",
    }
