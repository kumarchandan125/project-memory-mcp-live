import logging

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from project_memory_mcp_live.database import get_session
from project_memory_mcp_live.schemas.project import (
    ProjectCreate,
    ProjectUpdateInput,
    ProjectResponse,
)
from project_memory_mcp_live.services.project_services import ProjectService
from project_memory_mcp_live.services.exceptions import (
    ApplicationError,
)

logger = logging.getLogger(__name__)


def register_project_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def create_project(
        name: str,
        description: str | None = None,
        tech_stack: list[str] | None = None,
    ) -> dict:
        """
        Create and persist a new software project.

        Use this when the user introduces a new project and provides
        its name, description, or technology stack.
        """
        try:
            data = ProjectCreate(
                name=name,
                description=description,
                tech_stack=tech_stack or [],
            )

            async with get_session() as session:
                service = ProjectService(session)
                project = await service.create_project(data)

                result = ProjectResponse.model_validate(project)
                return {
                    "success": True,
                    "message": "Project created successfully.",
                    "project": result.model_dump(mode="json"),
                }

        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc

        except Exception as exc:
            logger.exception("Failed to create project")
            raise ToolError(
                "An unexpected error occurred while creating the project."
            ) from exc

    @mcp.tool()
    async def list_projects() -> dict:
        """
        List all saved software projects.

        Use this when the user asks which projects are saved,
        what they are working on, or wants an overview of projects.
        """
        try:
            async with get_session() as session:
                service = ProjectService(session)
                projects = await service.list_projects()

                items = [
                    ProjectResponse.model_validate(project).model_dump(
                        mode="json"
                    )
                    for project in projects
                ]

                return {
                    "success": True,
                    "count": len(items),
                    "projects": items,
                }

        except Exception as exc:
            logger.exception("Failed to list projects")
            raise ToolError(
                "Unable to retrieve the project list."
            ) from exc

    @mcp.tool()
    async def get_project_details(project_name: str) -> dict:
        """
        Retrieve complete saved details for a project.

        Use this when the user asks about a specific project's
        description, status, or technology stack.
        """
        try:
            async with get_session() as session:
                service = ProjectService(session)
                project = await service.get_project(project_name)

                result = ProjectResponse.model_validate(project)

                return {
                    "success": True,
                    "project": result.model_dump(mode="json"),
                }

        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc

        except Exception as exc:
            logger.exception("Failed to retrieve project details")
            raise ToolError(
                "Unable to retrieve the requested project."
            ) from exc

    @mcp.tool()
    async def update_project(
        project_name: str,
        changes: ProjectUpdateInput,
    ) -> dict:
        """
        Update saved project information.

        Use this when the user changes a project's name, description,
        technology stack, or status. Only include fields the user
        actually wants to change.
        """
        try:
            async with get_session() as session:
                service = ProjectService(session)
                project = await service.update_project(
                    project_name,
                    changes,
                )

                result = ProjectResponse.model_validate(project)

                return {
                    "success": True,
                    "message": "Project updated successfully.",
                    "project": result.model_dump(mode="json"),
                }

        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc

        except Exception as exc:
            logger.exception("Failed to update project")
            raise ToolError(
                "Unable to update the requested project."
            ) from exc