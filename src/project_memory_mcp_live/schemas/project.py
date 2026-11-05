from pydantic import BaseModel, ConfigDict, Field

from project_memory_mcp_live.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    """Validation schema for creating a project."""

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    tech_stack: list[str] = Field(
        default_factory=list,
        max_length=30,
    )


class ProjectUpdateInput(BaseModel):
    """Validation schema for updating a project."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    tech_stack: list[str] | None = Field(
        default=None,
        max_length=30,
    )

    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    """Response schema for project information."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: ProjectStatus
    tech_stack: list[str]
