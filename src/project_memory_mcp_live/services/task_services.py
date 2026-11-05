from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.task import (
    Task,
    TaskPriority,
    TaskStatus,
)
from project_memory_mcp_live.repositories import (
    ProjectRepository,
    TaskRepository,
)
from project_memory_mcp_live.schemas.task import (
    TaskCreate,
    TaskUpdateInput,
)


class TaskService:
    """Business logic for project tasks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repository = TaskRepository(session)
        self.project_repository = ProjectRepository(session)

    async def create_task(
        self,
        project_id: UUID,
        data: TaskCreate,
    ) -> Task:
        """Create a task for an existing project."""

        async with self.session.begin():
            project = await self.project_repository.get_by_id(
                project_id
            )

            if project is None:
                raise ValueError("Project not found.")

            return await self.task_repository.create(
                project_id=project_id,
                title=data.title,
                description=data.description,
                priority=data.priority,
            )

    async def get_task(self, task_id: UUID) -> Task:
        """Retrieve a task by UUID."""

        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        return task

    async def list_tasks(
        self,
        project_id: UUID,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> list[Task]:
        """List tasks with optional filters."""

        return await self.task_repository.get_by_project(
            project_id=project_id,
            status=status,
            priority=priority,
        )

    async def update_task(
        self,
        task_id: UUID,
        data: TaskUpdateInput,
    ) -> Task:
        """Update an existing task."""

        async with self.session.begin():
            task = await self.task_repository.get_by_id(task_id)

            if task is None:
                raise ValueError("Task not found.")

            changes = data.model_dump(exclude_unset=True)

            for field, value in changes.items():
                setattr(task, field, value)

            await self.session.flush()

            return task

    async def delete_task(self, task_id: UUID) -> None:
        """Delete an existing task."""

        async with self.session.begin():
            task = await self.task_repository.get_by_id(task_id)

            if task is None:
                raise ValueError("Task not found.")

            await self.task_repository.delete(task)