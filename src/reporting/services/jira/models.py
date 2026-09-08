from dataclasses import dataclass
from enum import StrEnum

from reporting.database.models import Task

_PROJECT_SEPARATOR = ", "


@dataclass(frozen=True)
class JiraMergedTask:
    description: str
    key: str
    tasks: tuple[Task, ...]
    texts: tuple[str, ...]

    @property
    def logged_rounded(self) -> int:
        return sum(task.logged_rounded for task in self.tasks)

    @property
    def project_names(self) -> str:
        return _PROJECT_SEPARATOR.join(dict.fromkeys(task.project.name for task in self.tasks))


class JiraTaskStatus(StrEnum):
    FAILED = "failed"
    SENT = "sent"


@dataclass(frozen=True)
class JiraTaskResult:
    status: JiraTaskStatus
    merged_task: JiraMergedTask
    reason: str = ""
