from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    @model_validator(mode="after")
    def reject_null_non_nullable_fields(self) -> Self:
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Project name cannot be null.")
        if "tech_stack" in self.model_fields_set and self.tech_stack is None:
            raise ValueError("Project tech_stack cannot be null.")
        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("Project status cannot be null.")
        return self


class ProjectResponse(BaseModel):
    """Response schema for project information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    status: ProjectStatus
    tech_stack: list[str]
