import logging
from uuid import UUID

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from project_memory_mcp_live.database import get_session
from project_memory_mcp_live.models.task import TaskPriority, TaskStatus
from project_memory_mcp_live.schemas.task import TaskCreate, TaskUpdateInput, TaskResponse
from project_memory_mcp_live.services.task_services import TaskService
from project_memory_mcp_live.services.exceptions import ApplicationError

logger = logging.getLogger(__name__)


def register_task_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def create_task(
        project_name: str,
        title: str,
        description: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> dict:
        """
        Create a task under an existing project.

        Use this when the user mentions something they need to implement,
        fix, investigate, or complete for a project.
        """
        try:
            data = TaskCreate(
                title=title,
                description=description,
                priority=priority,
            )

            async with get_session() as session:
                service = TaskService(session)
                task = await service.create_task_for_project(
                    project_name,
                    data,
                )

                result = TaskResponse.model_validate(task)

                return {
                    "success": True,
                    "message": "Task created successfully.",
                    "task": result.model_dump(mode="json"),
                }

        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to create task")
            raise ToolError("Unable to create the task.") from exc

    @mcp.tool()
    async def list_tasks(
        project_name: str,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> dict:
        """
        List tasks belonging to a project.

        Optionally filter by task status or priority.
        Use this when the user asks what work is pending,
        in progress, completed, or urgent.
        """
        try:
            async with get_session() as session:
                # Resolve the project using a separate service session.
                # This tool uses one session for its read-only operation.
                from project_memory_mcp_live.repositories import ProjectRepository

                project = await ProjectRepository(session).get_by_name(
                    project_name
                )

                if project is None:
                    raise ToolError(
                        f"Project '{project_name}' was not found."
                    )

                service = TaskService(session)
                tasks = await service.list_tasks(
                    project_id=project.id,
                    status=status,
                    priority=priority,
                )

                items = [
                    TaskResponse.model_validate(task).model_dump(
                        mode="json"
                    )
                    for task in tasks
                ]

                return {
                    "success": True,
                    "count": len(items),
                    "tasks": items,
                }

        except ToolError:
            raise
        except Exception as exc:
            logger.exception("Failed to list tasks")
            raise ToolError("Unable to retrieve project tasks.") from exc

    @mcp.tool()
    async def update_task(
        task_id: UUID,
        changes: TaskUpdateInput,
    ) -> dict:
        """
        Update a task's title, description, priority, or status.

        Use this when the user reports progress on an existing task,
        such as starting work or completing it.
        """
        try:
            async with get_session() as session:
                service = TaskService(session)
                task = await service.update_task(task_id, changes)

                result = TaskResponse.model_validate(task)

                return {
                    "success": True,
                    "message": "Task updated successfully.",
                    "task": result.model_dump(mode="json"),
                }

        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to update task")
            raise ToolError("Unable to update the task.") from exc