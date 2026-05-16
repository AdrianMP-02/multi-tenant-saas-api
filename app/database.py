from __future__ import annotations

import re
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateSchema, DropSchema

from app.config import settings

SCHEMA_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{0,62}$")


def validate_schema_name(schema_name: str) -> str:
    if schema_name == "public":
        return schema_name
    if not SCHEMA_NAME_RE.match(schema_name):
        raise ValueError(f"Invalid schema name: {schema_name!r}")
    return schema_name


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool if settings.is_development else None,
    **({} if settings.is_development else {"pool_size": 5, "max_overflow": 10}),
)

session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_engine():
    return engine


async def close_engine():
    await engine.dispose()


@asynccontextmanager
async def get_db(schema_name: str = "public") -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        schema_name = validate_schema_name(schema_name)
        if schema_name != "public":
            quoted = session.bind.dialect.identifier_preparer.quote_schema(schema_name)
            await session.execute(text(f"SET search_path TO {quoted}, public"))
        try:
            yield session
        finally:
            await session.close()


async def create_schema(schema_name: str) -> None:
    schema_name = validate_schema_name(schema_name)
    async with engine.begin() as conn:
        await conn.execute(CreateSchema(schema_name, if_not_exists=True))
        quoted = conn.dialect.identifier_preparer.quote_schema(schema_name)
        await conn.execute(text(f"SET search_path TO {quoted}, public"))
        await conn.run_sync(Base.metadata.create_all)


async def drop_schema(schema_name: str) -> None:
    schema_name = validate_schema_name(schema_name)
    async with engine.begin() as conn:
        await conn.execute(DropSchema(schema_name, cascade=True, if_exists=True))
