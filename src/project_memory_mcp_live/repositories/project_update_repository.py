import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.project_update import ProjectUpdate


class ProjectUpdateRepository:
    """Database operations for project updates."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        project_id: uuid.UUID,
        content: str,
    ) -> ProjectUpdate:
        """Create a development update."""

        update = ProjectUpdate(
            project_id=project_id,
            content=content,
        )

        self.session.add(update)
        await self.session.flush()

        return update

    async def get_by_id(
        self,
        update_id: uuid.UUID,
    ) -> ProjectUpdate | None:
        """Retrieve an update by its UUID."""

        statement = select(ProjectUpdate).where(
            ProjectUpdate.id == update_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: uuid.UUID,
        limit: int = 50,
    ) -> list[ProjectUpdate]:
        """Retrieve updates belonging to a project."""

        statement = (
            select(ProjectUpdate)
            .where(ProjectUpdate.project_id == project_id)
            .order_by(ProjectUpdate.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def delete(
        self,
        update: ProjectUpdate,
    ) -> None:
        """Delete a project update."""

        await self.session.delete(update)
        await self.session.flush()