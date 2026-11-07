from types import SimpleNamespace
from uuid import uuid4

from project_memory_mcp_live.models.project import ProjectStatus
from project_memory_mcp_live.schemas.project import ProjectResponse


def test_project_response_serializes_uuid_id_as_string():
    project_id = uuid4()
    project = SimpleNamespace(
        id=project_id,
        name="Test project",
        description=None,
        status=ProjectStatus.ACTIVE,
        tech_stack=[],
    )

    response = ProjectResponse.model_validate(project)

    assert response.id == project_id
    assert response.model_dump(mode="json")["id"] == str(project_id)
