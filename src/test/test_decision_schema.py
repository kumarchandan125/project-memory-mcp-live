from types import SimpleNamespace
from uuid import uuid4

from project_memory_mcp_live.schemas.decision import DecisionResponse


def test_decision_response_serializes_uuid_ids_as_strings():
    decision_id = uuid4()
    project_id = uuid4()
    decision = SimpleNamespace(
        id=decision_id,
        project_id=project_id,
        title="Database choice",
        decision="Use PostgreSQL",
        reasoning=None,
    )

    response = DecisionResponse.model_validate(decision)
    serialized = response.model_dump(mode="json")

    assert response.id == decision_id
    assert response.project_id == project_id
    assert serialized["id"] == str(decision_id)
    assert serialized["project_id"] == str(project_id)
