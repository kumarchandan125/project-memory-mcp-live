from __future__ import annotations

from typing import Final

from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from project_memory_mcp_live.config import get_settings

_ENGINE: AsyncEngine | None = None

_SUPPORTED_POSTGRES_DRIVERS: Final[frozenset[str]] = frozenset(
    {
        "postgres",
        "postgresql",
        "postgresql+psycopg",
        "postgresql+psycopg2",
        "postgresql+asyncpg",
    }
)


def build_async_database_url(database_url: str) -> URL:
    """Normalize a PostgreSQL URL for SQLAlchemy's async psycopg driver."""

    url = make_url(database_url)
    drivername = url.drivername.lower()

    if drivername in {"postgres", "postgresql"}:
        return url.set(drivername="postgresql+psycopg")

    if drivername not in _SUPPORTED_POSTGRES_DRIVERS:
        raise ValueError(
            "Unsupported PostgreSQL database URL scheme. "
            "Expected a PostgreSQL URL using postgres or postgresql."
        )

    return url.set(drivername="postgresql+psycopg")


def get_engine() -> AsyncEngine:
    """Create and reuse a singleton async database engine."""

    global _ENGINE

    if _ENGINE is not None:
        return _ENGINE

    settings = get_settings()
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    database_url = build_async_database_url(settings.database_url.get_secret_value())

    _ENGINE = create_async_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=settings.app_env == "development",
    )

    return _ENGINE


async def check_database_connection() -> None:
    """Verify that PostgreSQL is reachable and accepting connections."""

    engine = get_engine()
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_database() -> None:
    """Dispose of the shared database connection pool."""

    global _ENGINE

    if _ENGINE is not None:
        await _ENGINE.dispose()
        _ENGINE = None
