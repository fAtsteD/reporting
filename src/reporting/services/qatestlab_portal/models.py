from dataclasses import dataclass
from enum import StrEnum

from reporting.database.models import Task


@dataclass(frozen=True)
class PortalMergedTask:
    description: str
    key: str
    tasks: tuple[Task, ...]
    texts: tuple[str, ...]

    @property
    def logged_rounded(self) -> int:
        return sum(task.logged_rounded for task in self.tasks)

    @property
    def project_names(self) -> str:
        return self.tasks[0].project.name


class PortalTaskStatus(StrEnum):
    FAILED = "failed"
    SENT = "sent"


@dataclass(frozen=True)
class PortalTaskResult:
    status: PortalTaskStatus
    merged_task: PortalMergedTask
    reason: str = ""
