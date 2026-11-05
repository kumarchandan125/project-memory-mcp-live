from pydantic import BaseModel, ConfigDict, Field

from project_memory_mcp_live.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdateInput(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    priority: TaskPriority | None = None

    status: TaskStatus | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority