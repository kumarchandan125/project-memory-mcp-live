from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.project import Project
from project_memory_mcp_live.repositories import ProjectRepository
from project_memory_mcp_live.schemas.project import (
    ProjectCreate,
    ProjectUpdateInput,
)


class ProjectAlreadyExistsError(Exception):
    """Raised when a project with the same name exists."""


class ProjectNotFoundError(Exception):
    """Raised when a project cannot be found."""


class ProjectService:
    """Business logic for project operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = ProjectRepository(session)
        self.session = session

    async def create_project(
        self,
        data: ProjectCreate,
    ) -> Project:
        """Validate uniqueness and create a project."""

        async with self.session.begin():
            existing = await self.repository.get_by_name(
                data.name
            )

            if existing is not None:
                raise ProjectAlreadyExistsError(
                    f"Project '{data.name}' already exists."
                )

            project = await self.repository.create(
                name=data.name,
                description=data.description,
                tech_stack=data.tech_stack,
            )

            return project

    async def get_project(
        self,
        project_name: str,
    ) -> Project:
        """Retrieve a project by name."""

        project = await self.repository.get_by_name(
            project_name
        )

        if project is None:
            raise ProjectNotFoundError(
                f"Project '{project_name}' was not found."
            )

        return project

    async def list_projects(self) -> list[Project]:
        """Retrieve all projects."""

        return await self.repository.get_all()

    async def update_project(
        self,
        project_name: str,
        data: ProjectUpdateInput,
    ) -> Project:
        """Update an existing project."""

        async with self.session.begin():
            project = await self.repository.get_by_name(
                project_name
            )

            if project is None:
                raise ProjectNotFoundError(
                    f"Project '{project_name}' was not found."
                )

            changes = data.model_dump(exclude_unset=True)

            if "name" in changes and changes["name"] is not None:
                existing = await self.repository.get_by_name(
                    changes["name"]
                )

                if existing is not None and existing.id != project.id:
                    raise ProjectAlreadyExistsError(
                        f"Project '{changes['name']}' already exists."
                    )

            for field, value in changes.items():
                setattr(project, field, value)

            await self.session.flush()

            return project

    async def delete_project(
        self,
        project_name: str,
    ) -> None:
        """Delete a project."""

        async with self.session.begin():
            project = await self.repository.get_by_name(
                project_name
            )

            if project is None:
                raise ProjectNotFoundError(
                    f"Project '{project_name}' was not found."
                )

            await self.repository.delete(project)