from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from project_memory_mcp_live.models.project import ProjectStatus
from project_memory_mcp_live.schemas.project import (
    ProjectResponse,
    ProjectUpdateInput,
)


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


@pytest.mark.parametrize(
    "changes",
    [
        {"name": None},
        {"tech_stack": None},
        {"status": None},
    ],
)
def test_project_update_rejects_null_non_nullable_fields(changes):
    with pytest.raises(ValidationError, match="cannot be null"):
        ProjectUpdateInput(**changes)


def test_project_update_allows_omitted_name():
    changes = ProjectUpdateInput(description="Updated description")

    assert changes.model_dump(exclude_unset=True) == {
        "description": "Updated description"
    }
