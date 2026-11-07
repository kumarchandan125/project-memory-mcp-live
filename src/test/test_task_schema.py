from types import SimpleNamespace
from uuid import uuid4

from project_memory_mcp_live.models.task import TaskPriority, TaskStatus
from project_memory_mcp_live.schemas.task import TaskResponse


def test_task_response_serializes_uuid_ids_as_strings():
    task_id = uuid4()
    project_id = uuid4()
    task = SimpleNamespace(
        id=task_id,
        project_id=project_id,
        title="Test task",
        description=None,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
    )

    response = TaskResponse.model_validate(task)
    serialized = response.model_dump(mode="json")

    assert response.id == task_id
    assert response.project_id == project_id
    assert serialized["id"] == str(task_id)
    assert serialized["project_id"] == str(project_id)
