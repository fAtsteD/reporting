import datetime

from sqlalchemy.orm import Session

from .dictionary import Dictionary
from .jira_config import JiraConfig
from .reporting_config import ReportingConfig


class config:
    """
    Hold all config vars

    One config for app, so all vars static.
    """
    # Actions
    show_date: str | datetime.date | None = None
    parse_days: int | None = None

    # Input
    input_file_hours = ""

    # Text
    text_indent = "  "
    dictionary = Dictionary()

    # Tasks
    default_kind = "Development"
    default_project = "Default"
    skip_tasks = []
    minute_round_to = 25

    # Jira
    jira = JiraConfig()

    # Reporting
    reporting = ReportingConfig()

    # Parameters for program
    work_day_hours = datetime.timedelta(hours=8, minutes=0)

    # SQLite
    sqlite_session: Session = None
    sqlite_database_path: str = './report.db'
