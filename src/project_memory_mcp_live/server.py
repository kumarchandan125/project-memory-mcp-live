
import asyncio
import logging
import sys

from fastmcp import FastMCP

from project_memory_mcp_live.auth import build_auth_verifier
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

auth = build_auth_verifier(settings)

if auth is None:
    logger.warning(
        "Authentication is disabled. "
        "APP_ENV=development is intended for local use only."
    )
else:
    logger.info("Bearer token authentication enabled.")


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


def cli() -> None:
    """Run the HTTP server from the installed console script."""
    if sys.platform == "win32":
        # Psycopg async connections require a compatible event loop on Windows.
        asyncio.run(
            main(),
            loop_factory=asyncio.SelectorEventLoop,
        )

    else:
        asyncio.run(main())


if __name__ == "__main__":
    cli()
