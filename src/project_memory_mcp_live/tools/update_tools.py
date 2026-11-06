import logging

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from project_memory_mcp_live.database import get_session
from project_memory_mcp_live.repositories import ProjectRepository
from project_memory_mcp_live.schemas.project_update import (
    ProjectUpdateCreate,
    ProjectUpdateResponse,
)
from project_memory_mcp_live.services.project_update_service import (
    ProjectUpdateService,
)
from project_memory_mcp_live.services.exceptions import ApplicationError

logger = logging.getLogger(__name__)


def register_update_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def add_project_update(
        project_name: str,
        content: str,
    ) -> dict:
        """
        Save a development progress update for a project.

        Use this when the user describes what they worked on,
        what they implemented, what they fixed, or what they learned.
        """
        try:
            data = ProjectUpdateCreate(content=content)

            async with get_session() as session:
                project = await ProjectRepository(session).get_by_name(
                    project_name
                )

                if project is None:
                    raise ToolError(
                        f"Project '{project_name}' was not found."
                    )

                # Use a fresh session for the write transaction.
                project_id = project.id

            async with get_session() as session:
                service = ProjectUpdateService(session)
                update = await service.add_update(project_id, data)

                result = ProjectUpdateResponse.model_validate(update)

                return {
                    "success": True,
                    "message": "Project update saved.",
                    "update": result.model_dump(mode="json"),
                }

        except ToolError:
            raise
        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to save project update")
            raise ToolError("Unable to save the project update.") from exc

    @mcp.tool()
    async def get_project_updates(
        project_name: str,
        limit: int = 20,
    ) -> dict:
        """
        Retrieve the development history of a project.

        Use this when the user asks what they worked on previously,
        wants a progress summary, or needs recent development history.
        """
        try:
            async with get_session() as session:
                project = await ProjectRepository(session).get_by_name(
                    project_name
                )

                if project is None:
                    raise ToolError(
                        f"Project '{project_name}' was not found."
                    )

                project_id = project.id

            async with get_session() as session:
                service = ProjectUpdateService(session)
                updates = await service.get_update_history(
                    project_id,
                    limit=limit,
                )

                items = [
                    ProjectUpdateResponse.model_validate(update).model_dump(
                        mode="json"
                    )
                    for update in updates
                ]

                return {
                    "success": True,
                    "count": len(items),
                    "updates": items,
                }

        except ToolError:
            raise
        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to retrieve project updates")
            raise ToolError("Unable to retrieve project history.") from exc