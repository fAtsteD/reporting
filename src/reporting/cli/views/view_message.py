from rich.panel import Panel
from rich.text import Text

from reporting.cli.views import layout, theme

NO_TARGET_MESSAGE = "Specify at least one target: --jira or --portal"
REPORT_CHANGED_MESSAGE = "Report changed, nothing was sent"
REPORT_NOT_FOUND_MESSAGE = "Report does not exist"
SEND_QUESTION = "You try to send report not today. Do you want send report? (y/n) "


def render_error(error: Exception) -> Panel:
    return layout.error_panel(Text(str(error)))


def render_failure_count(failure_count: int) -> Text:
    return Text(f"Failed tasks: {failure_count}", style=theme.STYLE_FAILURE)


def render_notice(message: str) -> Text:
    return Text(message)


def render_parsed_count(report_count: int) -> Text:
    return Text(f"Parsed {report_count}")


def render_setting(key: str, value: str) -> Text:
    return Text(f"{key} = {value}")
