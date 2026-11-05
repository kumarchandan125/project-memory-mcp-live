import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_memory_mcp_live.models.decision import Decision


class DecisionRepository:
    """Database operations for project decisions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        project_id: uuid.UUID,
        title: str,
        decision: str,
        reasoning: str | None = None,
    ) -> Decision:
        """Record a technical decision."""

        record = Decision(
            project_id=project_id,
            title=title,
            decision=decision,
            reasoning=reasoning,
        )

        self.session.add(record)
        await self.session.flush()

        return record

    async def get_by_id(
        self,
        decision_id: uuid.UUID,
    ) -> Decision | None:
        """Retrieve a decision by UUID."""

        statement = select(Decision).where(
            Decision.id == decision_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: uuid.UUID,
        limit: int = 50,
    ) -> list[Decision]:
        """Retrieve decisions belonging to a project."""

        statement = (
            select(Decision)
            .where(Decision.project_id == project_id)
            .order_by(Decision.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def delete(
        self,
        decision: Decision,
    ) -> None:
        """Delete a technical decision."""

        await self.session.delete(decision)
        await self.session.flush()