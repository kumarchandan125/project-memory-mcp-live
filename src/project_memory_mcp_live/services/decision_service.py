from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.decision import Decision
from project_memory_mcp_live.repositories import (
    DecisionRepository,
    ProjectRepository,
)
from project_memory_mcp_live.schemas.decision import DecisionCreate


class DecisionService:
    """Business logic for technical decisions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.decision_repository = DecisionRepository(session)
        self.project_repository = ProjectRepository(session)

    async def record_decision(
        self,
        project_id: UUID,
        data: DecisionCreate,
    ) -> Decision:
        """Record a technical decision."""

        async with self.session.begin():
            project = await self.project_repository.get_by_id(
                project_id
            )

            if project is None:
                raise ValueError("Project not found.")

            return await self.decision_repository.create(
                project_id=project_id,
                title=data.title,
                decision=data.decision,
                reasoning=data.reasoning,
            )

    async def get_decisions(
        self,
        project_id: UUID,
        limit: int = 50,
    ) -> list[Decision]:
        """Retrieve project decisions."""

        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100.")

        project = await self.project_repository.get_by_id(
            project_id
        )

        if project is None:
            raise ValueError("Project not found.")

        return await self.decision_repository.get_by_project(
            project_id=project_id,
            limit=limit,
        )