import asyncio
import sys

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from project_memory_mcp_live.config import get_settings
from project_memory_mcp_live.database import build_async_database_url
from project_memory_mcp_live.models import Base


def pytest_asyncio_loop_factories(config, item):
    """Use a selector loop on Windows for Psycopg async connections."""

    if sys.platform == "win32":
        return {"windows-selector": asyncio.SelectorEventLoop}

    return {"default": asyncio.new_event_loop}


@pytest.fixture(scope="session")
def test_database_url():
    settings = get_settings()

    if settings.test_database_url is None:
        pytest.fail(
            "TEST_DATABASE_URL is required. "
            "Configure a dedicated test database before running integration tests."
        )

    test_url = build_async_database_url(settings.test_database_url.get_secret_value())

    if settings.database_url is not None:
        production_url = build_async_database_url(
            settings.database_url.get_secret_value()
        )

        if test_url == production_url:
            pytest.fail("TEST_DATABASE_URL must not point to the production database.")

    return test_url


@pytest.fixture
async def db_engine(test_database_url):
    engine = create_async_engine(
        test_database_url,
        pool_pre_ping=True,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def session_factory(db_engine):
    return async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
