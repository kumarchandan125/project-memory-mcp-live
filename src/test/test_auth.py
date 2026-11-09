import pytest
from pydantic import SecretStr

from project_memory_mcp_live.auth import (
    ProjectMemoryTokenVerifier,
    build_auth_verifier,
)
from project_memory_mcp_live.config import Settings


def test_authentication_is_disabled_only_in_explicit_development(monkeypatch):
    monkeypatch.delenv("AUTH_TOKEN", raising=False)

    assert (
        build_auth_verifier(
            Settings(_env_file=None, app_env="development")
        )
        is None
    )

    for app_env in ("test", "production"):
        with pytest.raises(RuntimeError, match="AUTH_TOKEN must be configured"):
            build_auth_verifier(Settings(_env_file=None, app_env=app_env))


@pytest.mark.asyncio
async def test_token_verifier_accepts_only_the_configured_token():
    verifier = ProjectMemoryTokenVerifier("expected-token")

    assert await verifier.verify_token("expected-token") is not None
    assert await verifier.verify_token("incorrect-token") is None


def test_auth_verifier_is_built_when_token_is_configured():
    verifier = build_auth_verifier(
        Settings(
            _env_file=None,
            app_env="production",
            auth_token=SecretStr("expected-token"),
        )
    )

    assert isinstance(verifier, ProjectMemoryTokenVerifier)
