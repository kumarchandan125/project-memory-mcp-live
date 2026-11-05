import asyncio
import sys

import pytest

from project_memory_mcp_live.database import build_async_database_url


@pytest.mark.asyncio
async def test_windows_uses_selector_event_loop():
    if sys.platform == "win32":
        assert isinstance(
            asyncio.get_running_loop(),
            asyncio.SelectorEventLoop,
        )


def test_postgres_url_uses_psycopg_driver():
    url = build_async_database_url("postgresql://user:password@localhost:5432/testdb")
    assert url.drivername == "postgresql+psycopg"


def test_existing_psycopg_url_is_preserved():
    url = build_async_database_url(
        "postgresql+psycopg://user:password@localhost:5432/testdb"
    )
    assert url.drivername == "postgresql+psycopg"
