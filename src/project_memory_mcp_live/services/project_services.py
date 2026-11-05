from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.project import Project
from project_memory_mcp_live.repositories import ProjectRepository
from project_memory_mcp_live.schemas.project import (
    ProjectCreate,
    ProjectUpdateInput,
)
from project_memory_mcp_live.services.exceptions import (
    DuplicateProjectError,
    ProjectNotFoundError,
)

_PROJECT_NAME_INDEX = "ix_projects_name"


def _is_project_name_conflict(error: IntegrityError) -> bool:
    """Return whether a PostgreSQL error is the project-name unique conflict."""

    original_error = error.orig
    diagnostic = getattr(original_error, "diag", None)
    return (
        getattr(original_error, "sqlstate", None) == "23505"
        and getattr(diagnostic, "constraint_name", None) == _PROJECT_NAME_INDEX
    )


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

        try:
            async with self.session.begin():
                existing = await self.repository.get_by_name(data.name)

                if existing is not None:
                    raise DuplicateProjectError(data.name)

                project = await self.repository.create(
                    name=data.name,
                    description=data.description,
                    tech_stack=data.tech_stack,
                )

                return project
        except IntegrityError as exc:
            if _is_project_name_conflict(exc):
                raise DuplicateProjectError(data.name) from exc
            raise

    async def get_project(
        self,
        project_name: str,
    ) -> Project:
        """Retrieve a project by name."""

        project = await self.repository.get_by_name(project_name)

        if project is None:
            raise ProjectNotFoundError(project_name)

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

        try:
            async with self.session.begin():
                project = await self.repository.get_by_name(project_name)

                if project is None:
                    raise ProjectNotFoundError(project_name)

                changes = data.model_dump(exclude_unset=True)

                if "name" in changes and changes["name"] is not None:
                    existing = await self.repository.get_by_name(changes["name"])

                    if existing is not None and existing.id != project.id:
                        raise DuplicateProjectError(changes["name"])

                for field, value in changes.items():
                    setattr(project, field, value)

                await self.session.flush()

                return project
        except IntegrityError as exc:
            if data.name is not None and _is_project_name_conflict(exc):
                raise DuplicateProjectError(data.name) from exc
            raise

    async def delete_project(
        self,
        project_name: str,
    ) -> None:
        """Delete a project."""

        async with self.session.begin():
            project = await self.repository.get_by_name(project_name)

            if project is None:
                raise ProjectNotFoundError(project_name)

            await self.repository.delete(project)
