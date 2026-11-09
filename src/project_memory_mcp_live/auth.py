import secrets

from fastmcp.server.auth import AccessToken, TokenVerifier


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