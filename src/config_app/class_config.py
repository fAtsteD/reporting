import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from models import Base

from .dictionary import Dictionary
from .jira_config import JiraConfig
from .reporting_config import ReportingConfig


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
class Config:
    """
    Hold all config vars

    One config for app, so all vars static.
    """

    commands: list[Command] = field(default_factory=lambda: [])

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

    # Text
    dictionary = Dictionary()

    # Tasks
    default_kind = "Development"
    default_project = "Default"
    minute_round_to = 25
    skip_tasks: list[str] = field(default_factory=lambda: [])

    # Jira
    jira = JiraConfig()

    # Reporting
    reporting = ReportingConfig()

    # Parameters for program
    work_day_hours = datetime.timedelta(hours=8, minutes=0)

    # SQLite
    sqlite_database_path = Path("./report.db")

    def __post_init__(self) -> None:
        self._engine: Engine | None = None
        self._session: Session | None = None

    @property
    def sqlite_session(self) -> Session:
        database_url = "sqlite:///" + str(self.sqlite_database_path)
        if (
            self._session is None
            or not isinstance(self._session.bind, Engine)
            or str(self._session.bind.url) != database_url
        ):
            sqlalchemy_engine = create_engine(database_url, echo=False)
            Base.metadata.create_all(sqlalchemy_engine)
            self._session = Session(bind=sqlalchemy_engine)
        return self._session
