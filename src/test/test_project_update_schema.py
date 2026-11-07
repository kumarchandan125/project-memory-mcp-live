from types import SimpleNamespace
from uuid import uuid4

from project_memory_mcp_live.schemas.project_update import ProjectUpdateResponse


def test_project_update_response_serializes_uuid_ids_as_strings():
    update_id = uuid4()
    project_id = uuid4()
    update = SimpleNamespace(
        id=update_id,
        project_id=project_id,
        content="Implemented feature",
    )

    response = ProjectUpdateResponse.model_validate(update)
    serialized = response.model_dump(mode="json")

    assert response.id == update_id
    assert response.project_id == project_id
    assert serialized["id"] == str(update_id)
    assert serialized["project_id"] == str(project_id)
