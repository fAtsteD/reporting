from dataclasses import dataclass
from enum import StrEnum

from reporting.database.models import Task


class JiraTaskStatus(StrEnum):
    FAILED = "failed"
    SENT = "sent"


@dataclass(frozen=True)
class JiraTaskResult:
    status: JiraTaskStatus
    task: Task
    reason: str = ""
