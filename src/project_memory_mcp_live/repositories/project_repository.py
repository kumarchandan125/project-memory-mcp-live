import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.project import Project, ProjectStatus


class ProjectRepository:
    """Database operations for projects."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        name: str,
        description: str | None = None,
        tech_stack: list[str] | None = None,
    ) -> Project:
        """Create a new project."""

        project = Project(
            name=name,
            description=description,
            tech_stack=list(tech_stack) if tech_stack is not None else [],
        )

        self.session.add(project)

        await self.session.flush()

        return project

    async def get_by_id(
        self,
        project_id: uuid.UUID,
    ) -> Project | None:
        """Find a project using its UUID."""

        statement = select(Project).where(
            Project.id == project_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Project | None:
        """Find a project using its name."""

        statement = select(Project).where(
            Project.name == name
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        """Return all projects, optionally filtered by status."""

        statement = select(Project).order_by(
            Project.created_at.desc()
        )

        if status is not None:
            statement = statement.where(
                Project.status == status
            )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        project: Project,
        *,
        name: str | None = None,
        description: str | None = None,
        tech_stack: list[str] | None = None,
        status: ProjectStatus | None = None,
    ) -> Project:
        """Update the provided project fields."""

        if name is not None:
            project.name = name

        if description is not None:
            project.description = description

        if tech_stack is not None:
            project.tech_stack = list(tech_stack)

        if status is not None:
            project.status = status

        await self.session.flush()

        return project

    async def delete(self, project: Project) -> None:
        """Delete a project."""

        await self.session.delete(project)

        await self.session.flush()