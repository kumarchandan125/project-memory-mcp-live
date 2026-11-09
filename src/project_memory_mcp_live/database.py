from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from project_memory_mcp_live.config import get_settings

_engine: AsyncEngine | None = None

_session_factory: async_sessionmaker[AsyncSession] | None = None


def build_async_database_url(database_url: str) -> URL:
    """Convert a PostgreSQL URL to the Psycopg driver URL."""

    url = make_url(database_url)
    drivername = url.drivername.lower()

    if drivername in ("postgres", "postgresql"):
        return url.set(drivername="postgresql+psycopg")

    if drivername == "postgresql+psycopg":
        return url.set(drivername="postgresql+psycopg")

    raise ValueError(
        "Unsupported database URL scheme. "
        "Expected postgres, postgresql, or postgresql+psycopg."
    )


def get_engine() -> AsyncEngine:
    """Create or return the shared asynchronous database engine."""

    global _engine

    if _engine is None:
        settings = get_settings()

        if settings.database_url is None:
            raise RuntimeError("DATABASE_URL is not configured.")

        database_url = build_async_database_url(
            settings.database_url.get_secret_value()
        )

        _engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=2,
            pool_recycle=1800,
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create or return the shared async session factory."""

    global _session_factory

    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide a fresh database session for one operation."""
    session_factory = get_session_factory()

    async with session_factory() as session:
        yield session


async def check_database_connection() -> None:
    """Verify that the database connection is working."""

    engine = get_engine()

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_database() -> None:
    """Dispose of the engine and reset database resources."""

    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _session_factory = None
