from dataclasses import dataclass
from enum import StrEnum

from reporting.database.models import Task


class PortalTaskStatus(StrEnum):
    FAILED = "failed"
    SENT = "sent"


@dataclass(frozen=True)
class PortalTaskResult:
    status: PortalTaskStatus
    task: Task
    reason: str = ""
