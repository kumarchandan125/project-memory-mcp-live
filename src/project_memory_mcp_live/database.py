
from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from project_memory_mcp_live.config import get_settings


_engine: AsyncEngine | None = None


def build_async_database_url(database_url: str) -> URL:
    """Convert a standard PostgreSQL URL to the Psycopg driver URL."""

    url = make_url(database_url)

    if url.drivername in ("postgres", "postgresql"):
        return url.set(drivername="postgresql+psycopg")

    if url.drivername == "postgresql+psyg":
        return url

    raise ValueError("Unsupported PostgreSQL database URL scheme.")


def get_engine() -> AsyncEngine:
    """Create and reuse the asynchronous database engine."""

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


async def check_database_connection() -> None:
    """Verify that PostgreSQL is reachable."""

    engine = get_engine()

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_database() -> None:
    """Dispose of the database connection pool."""

    global _engine

    if _engine is not None:
        await _engine.dispose()
        _engine = None
