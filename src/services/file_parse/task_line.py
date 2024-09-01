from dataclasses import dataclass
from datetime import datetime


@dataclass()
class TaskLine:
    """
    Simple dto for structure parsed line of task
    """

    time_begin: datetime | None = None
    summary: str = ""
    kind: str = ""
    project: str = ""
