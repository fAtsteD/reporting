import datetime
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo


@dataclass
class AppConfig:
    program_dir = Path("~/.reporting").expanduser()

    input_file_hours = ""
    timezone_name: str | None = None

    default_kind = "Development"
    default_project = "Default"
    minute_round_to = 15
    skip_tasks: list[str] = field(default_factory=list)

    work_day_hours = datetime.timedelta(hours=8, minutes=0)

    @property
    def timezone(self) -> datetime.tzinfo:
        if self.timezone_name:
            return ZoneInfo(self.timezone_name)

        return datetime.datetime.now().astimezone().tzinfo or datetime.UTC
