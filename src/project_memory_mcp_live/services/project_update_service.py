from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.project_update import ProjectUpdate
from project_memory_mcp_live.repositories import (
    ProjectRepository,
    ProjectUpdateRepository,
)
from project_memory_mcp_live.schemas.project_update import (
    ProjectUpdateCreate,
)
from project_memory_mcp_live.services.exceptions import(
    ProjectNotFoundError
)

class ProjectUpdateService:
    """Business logic for development progress."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.update_repository = ProjectUpdateRepository(session)
        self.project_repository = ProjectRepository(session)

    async def add_update(
        self,
        project_id: UUID,
        data: ProjectUpdateCreate,
    ) -> ProjectUpdate:
        """Save a development update."""

        async with self.session.begin():
            project = await self.project_repository.get_by_id(
                project_id
            )

            if project is None:
                raise ProjectNotFoundError(str(project_id))

            return await self.update_repository.create(
                project_id=project_id,
                content=data.content,
            )

    async def get_update_history(
        self,
        project_id: UUID,
        limit: int = 50,
    ) -> list[ProjectUpdate]:
        """Retrieve recent development updates."""

        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100.")

        project = await self.project_repository.get_by_id(
            project_id
        )

        if project is None:
            raise ProjectNotFoundError(str(project_id))

        return await self.update_repository.get_by_project(
            project_id=project_id,
            limit=limit,
        )