from project_memory_mcp_live.config import Settings


def test_default_settings(monkeypatch):
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_name == "Project Memory MCP Server"
    assert settings.app_env == "production"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
