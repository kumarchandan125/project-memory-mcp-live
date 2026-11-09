class ApplicationError(Exception):
    """Base exception for expected application-level errors."""


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource does not exist."""


class ProjectNotFoundError(ResourceNotFoundError):
    def __init__(self, project_name: str):
        self.project_name = project_name
        super().__init__(f"Project '{project_name}' was not found.")


class ProjectNotArchivedError(ApplicationError):
    def __init__(self, project_name: str):
        self.project_name = project_name
        super().__init__(
            f"Project '{project_name}' must be archived before it can be deleted."
        )


class TaskNotFoundError(ResourceNotFoundError):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task '{task_id}' was not found.")


class ProjectUpdateNotFoundError(ResourceNotFoundError):
    def __init__(self, update_id: str):
        self.update_id = update_id
        super().__init__(f"Project update '{update_id}' was not found.")


class DecisionNotFoundError(ResourceNotFoundError):
    def __init__(self, decision_id: str):
        self.decision_id = decision_id
        super().__init__(f"Decision '{decision_id}' was not found.")


class DuplicateProjectError(ApplicationError):
    def __init__(self, project_name: str):
        self.project_name = project_name
        super().__init__(f"A project named '{project_name}' already exists.")
