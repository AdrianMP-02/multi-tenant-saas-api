from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.database import close_engine, get_engine, session_factory
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.tenant_middleware import TenantMiddleware
from app.models.user import User


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await get_engine()

    async with session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == settings.default_admin_email)
        )
        if not result.scalar_one_or_none():
            admin = User(
                email=settings.default_admin_email,
                password_hash=hash_password(settings.default_admin_password),
                full_name="Super Admin",
                is_superadmin=True,
            )
            session.add(admin)
            await session.commit()

    yield
    await close_engine()


app = FastAPI(
    title="Multi-tenant SaaS API",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TenantMiddleware)

app.include_router(v1_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}
