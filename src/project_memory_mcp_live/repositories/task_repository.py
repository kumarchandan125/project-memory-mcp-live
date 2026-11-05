import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.task import (
    Task,
    TaskPriority,
    TaskStatus,
)


class TaskRepository:
    """Database operations for project tasks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        project_id: uuid.UUID,
        title: str,
        description: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> Task:
        """Create a new task."""

        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
        )

        self.session.add(task)
        await self.session.flush()

        return task

    async def get_by_id(
        self,
        task_id: uuid.UUID,
    ) -> Task | None:
        """Retrieve a task by UUID."""

        statement = select(Task).where(Task.id == task_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: uuid.UUID,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> list[Task]:
        """Retrieve tasks with optional filters."""

        statement = select(Task).where(Task.project_id == project_id)

        if status is not None:
            statement = statement.where(Task.status == status)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        statement = statement.order_by(Task.created_at.desc())

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def update_status(
        self,
        task: Task,
        status: TaskStatus,
    ) -> Task:
        """Change the status of a task."""

        task.status = status

        await self.session.flush()

        return task

    async def delete(
        self,
        task: Task,
    ) -> None:
        """Delete a task."""

        await self.session.delete(task)
        await self.session.flush()
