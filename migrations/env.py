import asyncio
import sys

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from project_memory_mcp_live.config import get_settings
from project_memory_mcp_live.database import build_async_database_url
from project_memory_mcp_live.models import Base

# Alembic configuration
config = context.config

# Target metadata for autogenerate
target_metadata = Base.metadata


def get_database_url() -> str:
    """Load the database URL from application settings."""

    settings = get_settings()

    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    database_url = build_async_database_url(
        settings.database_url.get_secret_value()
    )

    return database_url.render_as_string(
        hide_password=False
    )


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using an active database connection."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""

    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations using an asynchronous connection."""

    if sys.platform == "win32":
        asyncio.run(
            run_async_migrations(),
            loop_factory=asyncio.SelectorEventLoop,
        )
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()