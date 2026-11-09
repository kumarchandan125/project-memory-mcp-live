
import asyncio
import logging
import sys

from fastmcp import FastMCP
from fastmcp.server.auth import TokenVerifier

from project_memory_mcp_live.auth import ProjectMemoryTokenVerifier
from project_memory_mcp_live.config import get_settings
from project_memory_mcp_live.database import check_database_connection
from project_memory_mcp_live.tools import register_all_tools

# ========================= Configuration =========================

settings = get_settings()


# ========================= Logging ===============================

logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    ),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)

logger = logging.getLogger("project_memory_mcp_live.server")


# ========================= Authentication =======================

auth: TokenVerifier | None = None

if settings.app_env == "production":

    if settings.auth_token is None:
        raise RuntimeError(
            "AUTH_TOKEN must be configured in production."
        )

    auth = ProjectMemoryTokenVerifier(
        expected_token=settings.auth_token.get_secret_value()
    )

    logger.info("Production bearer token authentication enabled.")

else:
    logger.warning(
        "Authentication is disabled. "
        "This configuration is intended for local development only."
    )


# ========================= FastMCP Server ========================

mcp = FastMCP(
    settings.app_name,
    auth=auth,
    mask_error_details=True,
)


# ========================= Register Application Tools ===========

register_all_tools(mcp)


# ========================= Health Check ==========================

@mcp.tool
async def check_system_health() -> dict[str, str]:
    """Check the application and PostgreSQL connection status."""

    if settings.database_url is None:
        logger.warning(
            "Database configuration missing; health check degraded."
        )

        return {
            "application": "running",
            "database": "not_configured",
            "status": "degraded",
            "message": "Configure DATABASE_URL to enable database connectivity.",
        }

    try:
        await check_database_connection()

    except Exception:
        logger.exception("Database health check failed")

        return {
            "application": "running",
            "database": "unavailable",
            "status": "degraded",
            "message": "Database connection failed. Check server logs.",
        }

    return {
        "application": "running",
        "database": "connected",
        "status": "healthy",
        "message": "Application and database are working correctly.",
    }


# ========================= Server Startup ========================

async def main() -> None:
    """Start the FastMCP HTTP server."""

    logger.info("Starting %s...", settings.app_name)

    await mcp.run_async(
        transport="http",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":

    if sys.platform == "win32":
        # Psycopg async connections require a compatible event loop on Windows.
        asyncio.run(
            main(),
            loop_factory=asyncio.SelectorEventLoop,
        )

    else:
        asyncio.run(main())
