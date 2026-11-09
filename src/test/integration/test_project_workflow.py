from uuid import uuid4

import pytest

from project_memory_mcp_live.models.project import ProjectStatus
from project_memory_mcp_live.models.task import (
    TaskPriority,
    TaskStatus,
)
from project_memory_mcp_live.schemas.decision import DecisionCreate
from project_memory_mcp_live.schemas.project import (
    ProjectCreate,
    ProjectUpdateInput,
)
from project_memory_mcp_live.schemas.project_update import ProjectUpdateCreate
from project_memory_mcp_live.schemas.task import TaskCreate, TaskUpdateInput
from project_memory_mcp_live.services.decision_service import DecisionService
from project_memory_mcp_live.services.exceptions import (
    DuplicateProjectError,
    ProjectNotArchivedError,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from project_memory_mcp_live.services.project_services import ProjectService
from project_memory_mcp_live.services.project_update_service import ProjectUpdateService
from project_memory_mcp_live.services.task_services import TaskService


@pytest.mark.asyncio
async def test_complete_project_workflow(session_factory):
    # 1. Create a project
    async with session_factory() as session:
        project_service = ProjectService(session)

        project = await project_service.create_project(
            ProjectCreate(
                name="Grocery Delivery",
                description="A full-stack grocery delivery application.",
                tech_stack=["React", "Express", "PostgreSQL"],
            )
        )

        project_id = project.id

    # 2. Add a task
    async with session_factory() as session:
        task_service = TaskService(session)

        task = await task_service.create_task(
            project_id=project_id,
            data=TaskCreate(
                title="Implement Redis caching",
                description="Add caching for frequently requested products.",
                priority=TaskPriority.HIGH,
            ),
        )

        assert task.title == "Implement Redis caching"

    # 3. Record a development update
    async with session_factory() as session:
        update_service = ProjectUpdateService(session)

        update = await update_service.add_update(
            project_id=project_id,
            data=ProjectUpdateCreate(content="Configured the Redis connection."),
        )

        assert "Redis connection" in update.content

    # 4. Record an architectural decision
    async with session_factory() as session:
        decision_service = DecisionService(session)

        decision = await decision_service.record_decision(
            project_id=project_id,
            data=DecisionCreate(
                title="Database selection",
                decision="Use PostgreSQL with Neon.",
                reasoning="Managed PostgreSQL simplifies deployment.",
            ),
        )

        assert decision.title == "Database selection"

    # 5. Retrieve saved information
    async with session_factory() as session:
        task_service = TaskService(session)
        tasks = await task_service.list_tasks(project_id)

        assert len(tasks) == 1
        assert tasks[0].title == "Implement Redis caching"

    async with session_factory() as session:
        update_service = ProjectUpdateService(session)
        updates = await update_service.get_update_history(project_id)

        assert len(updates) == 1

    async with session_factory() as session:
        decision_service = DecisionService(session)
        decisions = await decision_service.get_decisions(project_id)

        assert len(decisions) == 1
        assert decisions[0].decision == "Use PostgreSQL with Neon."


@pytest.mark.asyncio
async def test_duplicate_project_is_rejected(session_factory):
    async with session_factory() as session:
        service = ProjectService(session)

        await service.create_project(ProjectCreate(name="Duplicate Test"))

    async with session_factory() as session:
        service = ProjectService(session)

        with pytest.raises(DuplicateProjectError):
            await service.create_project(ProjectCreate(name="Duplicate Test"))


@pytest.mark.asyncio
async def test_task_creation_with_missing_project_fails(session_factory):
    async with session_factory() as session:
        service = TaskService(session)

        with pytest.raises(ProjectNotFoundError):
            await service.create_task(
                project_id=uuid4(),
                data=TaskCreate(title="Test task"),
            )


@pytest.mark.asyncio
async def test_task_update_and_delete(session_factory):
    async with session_factory() as session:
        project = await ProjectService(session).create_project(
            ProjectCreate(name="Task lifecycle")
        )
        project_id = project.id

    async with session_factory() as session:
        service = TaskService(session)
        task = await service.create_task(
            project_id,
            TaskCreate(title="Original task"),
        )
        task_id = task.id

    async with session_factory() as session:
        task = await TaskService(session).update_task(
            task_id,
            TaskUpdateInput(
                title="Updated task",
                status=TaskStatus.IN_PROGRESS,
            ),
        )

        assert task.title == "Updated task"
        assert task.status == TaskStatus.IN_PROGRESS

    async with session_factory() as session:
        await TaskService(session).delete_task(task_id)

    async with session_factory() as session:
        with pytest.raises(TaskNotFoundError):
            await TaskService(session).get_task(task_id)


@pytest.mark.asyncio
async def test_project_must_be_archived_before_permanent_deletion(session_factory):
    async with session_factory() as session:
        project = await ProjectService(session).create_project(
            ProjectCreate(name="Archive before delete")
        )
        project_id = project.id

    async with session_factory() as session:
        await TaskService(session).create_task(
            project_id,
            TaskCreate(title="Preserved task"),
        )
        await DecisionService(session).record_decision(
            project_id,
            DecisionCreate(
                title="Preserved decision",
                decision="Keep the data until archive is confirmed.",
            ),
        )

    async with session_factory() as session:
        with pytest.raises(ProjectNotArchivedError):
            await ProjectService(session).delete_project("Archive before delete")

    async with session_factory() as session:
        tasks = await TaskService(session).list_tasks(project_id)
        decisions = await DecisionService(session).get_decisions(project_id)

        assert len(tasks) == 1
        assert len(decisions) == 1

    async with session_factory() as session:
        await ProjectService(session).update_project(
            "Archive before delete",
            ProjectUpdateInput(status=ProjectStatus.ARCHIVED),
        )

    async with session_factory() as session:
        await ProjectService(session).delete_project("Archive before delete")

    async with session_factory() as session:
        with pytest.raises(ProjectNotFoundError):
            await ProjectService(session).get_project("Archive before delete")
