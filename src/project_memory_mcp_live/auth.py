import secrets

from fastmcp.server.auth import AccessToken, TokenVerifier

from project_memory_mcp_live.config import Settings


class ProjectMemoryTokenVerifier(TokenVerifier):
    """Verify bearer tokens for the Project Memory MCP server."""

    def __init__(self, expected_token: str) -> None:
        super().__init__()
        self.expected_token = expected_token

    async def verify_token(self, token: str) -> AccessToken | None:
        """Validate the incoming bearer token."""

        if not secrets.compare_digest(token, self.expected_token):
            return None

        return AccessToken(
            token=token,
            client_id="project-memory-client",
            scopes=[],
            subject="project-memory-owner",
        )


def build_auth_verifier(settings: Settings) -> TokenVerifier | None:
    """Disable authentication only for explicitly configured development."""

    if settings.app_env == "development":
        return None

    if settings.auth_token is None:
        raise RuntimeError(
            "AUTH_TOKEN must be configured unless APP_ENV=development."
        )

    return ProjectMemoryTokenVerifier(
        expected_token=settings.auth_token.get_secret_value()
    )