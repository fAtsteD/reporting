import datetime
from dataclasses import dataclass


@dataclass
class TaskLine:
    time_begin: datetime.datetime
    summary: str = ""
    kind: str = ""
    project: str = ""
