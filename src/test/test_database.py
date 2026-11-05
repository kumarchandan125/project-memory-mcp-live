from project_memory_mcp_live.database import build_async_database_url


def test_postgres_url_uses_psycopg_driver():
    url = build_async_database_url("postgresql://user:password@localhost:5432/testdb")
    assert url.drivername == "postgresql+psycopg"


def test_existing_psycopg_url_is_preserved():
    url = build_async_database_url(
        "postgresql+psycopg://user:password@localhost:5432/testdb"
    )
    assert url.drivername == "postgresql+psycopg"
