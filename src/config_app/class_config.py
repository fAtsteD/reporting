import datetime

from .dictionary import Dictionary
from .jira_config import JiraConfig
from .reporting_config import ReportingConfig


class config:
    """
    Hold all config vars

    One config for app, so all vars static.
    """
    # Input
    input_file_hours = ""

    # Output
    outputs_day_report = []
    output_file_day = ""

    # Text
    file_type_print = 1
    console_type_print = 1
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
