import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Command(Enum):
    JIRA = "jira"
    KIND_SHOW = "show-kinds"
    KIND_UPDATE = "kind"
    PROJECT_SHOW = "show-projects"
    PROJECT_UPDATE = "project"
    REPORT_PARSE = "parse"
    REPORT_SHOW = "show"
    REPORTING = "reporting"


@dataclass
class AppConfig:
    """
    Hold all config vars

    One config for app, so all vars static.
    """

    # Directories
    program_dir = Path("~/.reporting").expanduser()

    # Actions
    parse_days: int | None = None
    show_date: str | datetime.date = "last"

    kind_data: dict = field(default_factory=lambda: {})
    show_kinds = False

    project_data: dict = field(default_factory=lambda: {})
    show_projects = False

    # Input
    input_file_hours = ""

    # Tasks
    default_kind = "Development"
    default_project = "Default"
    minute_round_to = 15
    skip_tasks: list[str] = field(default_factory=lambda: [])

    # Parameters for program
    work_day_hours = datetime.timedelta(hours=8, minutes=0)
