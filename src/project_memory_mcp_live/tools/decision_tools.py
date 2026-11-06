import logging

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from project_memory_mcp_live.database import get_session
from project_memory_mcp_live.repositories import ProjectRepository
from project_memory_mcp_live.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
)
from project_memory_mcp_live.services.decision_service import DecisionService
from project_memory_mcp_live.services.exceptions import ApplicationError

logger = logging.getLogger(__name__)


def register_decision_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def record_decision(
        project_name: str,
        title: str,
        decision: str,
        reasoning: str | None = None,
    ) -> dict:
        """
        Record an important technical or architectural decision.

        Use this when the user explicitly chooses a technology,
        architecture, design approach, or implementation strategy.
        Save the decision and its reasoning when available.
        """
        try:
            data = DecisionCreate(
                title=title,
                decision=decision,
                reasoning=reasoning,
            )

            async with get_session() as session:
                project = await ProjectRepository(session).get_by_name(
                    project_name
                )

                if project is None:
                    raise ToolError(
                        f"Project '{project_name}' was not found."
                    )

                project_id = project.id

            async with get_session() as session:
                service = DecisionService(session)
                decision_record = await service.record_decision(
                    project_id,
                    data,
                )

                result = DecisionResponse.model_validate(decision_record)

                return {
                    "success": True,
                    "message": "Decision recorded successfully.",
                    "decision": result.model_dump(mode="json"),
                }

        except ToolError:
            raise
        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to record decision")
            raise ToolError("Unable to record the decision.") from exc

    @mcp.tool()
    async def get_project_decisions(
        project_name: str,
        limit: int = 20,
    ) -> dict:
        """
        Retrieve saved technical and architectural decisions.

        Use this when the user asks why a technology was selected,
        what architecture was agreed upon, or what decisions were made.
        """
        try:
            async with get_session() as session:
                project = await ProjectRepository(session).get_by_name(
                    project_name
                )

                if project is None:
                    raise ToolError(
                        f"Project '{project_name}' was not found."
                    )

                project_id = project.id

            async with get_session() as session:
                service = DecisionService(session)
                decisions = await service.get_decisions(
                    project_id,
                    limit=limit,
                )

                items = [
                    DecisionResponse.model_validate(item).model_dump(
                        mode="json"
                    )
                    for item in decisions
                ]

                return {
                    "success": True,
                    "count": len(items),
                    "decisions": items,
                }

        except ToolError:
            raise
        except ApplicationError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to retrieve decisions")
            raise ToolError("Unable to retrieve project decisions.") from exc