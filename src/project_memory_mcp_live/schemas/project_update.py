from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectUpdateCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=10000,
    )


class ProjectUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    content: str
