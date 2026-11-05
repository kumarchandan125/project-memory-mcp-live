import logging

from fastmcp import FastMCP

from project_memory_mcp_live.config import get_settings
from project_memory_mcp_live.database import check_database_connection

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)

logger = logging.getLogger("project_memory_mcp_live.server")

mcp = FastMCP(settings.app_name)


@mcp.tool
async def check_system_health() -> dict[str, str]:
    """Check the application and PostgreSQL connection status."""

    if settings.database_url is None:
        logger.warning("Database configuration missing; health check degraded.")
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


def main() -> None:
    """Run the MCP HTTP server."""

    logger.info("Starting %s on %s:%s", settings.app_name, settings.host, settings.port)
    mcp.run(
        transport="http",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":
    main()
