import datetime
from collections.abc import Sequence

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from reporting.cli.views import formatting, layout, theme
from reporting.database.models import Task
from reporting.services.jira.models import JiraTaskResult, JiraTaskStatus
from reporting.services.qatestlab_portal.models import PortalTaskResult, PortalTaskStatus

CURRENT_DATE_LABEL = "Current date"
EMPTY_MESSAGE = "No tasks to send"
JIRA_PROGRESS_MESSAGE = "Sending to Jira..."
JIRA_TITLE = "Jira"
PORTAL_PROGRESS_MESSAGE = "Sending to QATestLab Portal..."
PORTAL_TITLE = "QATestLab Portal"
REPORT_DATE_LABEL = "Report date"


def render_date_mismatch(report_date: datetime.date, current_date: datetime.date) -> Table:
    return layout.definition_table(
        [
            (REPORT_DATE_LABEL, formatting.format_date(report_date)),
            (CURRENT_DATE_LABEL, formatting.format_date(current_date)),
        ]
    )


def render_jira_results(results: Sequence[JiraTaskResult]) -> Panel:
    rows = [(result.status is JiraTaskStatus.SENT, result.task, result.reason) for result in results]

    return _render(JIRA_TITLE, rows)


def render_portal_results(results: Sequence[PortalTaskResult]) -> Panel:
    rows = [(result.status is PortalTaskStatus.SENT, result.task, result.reason) for result in results]

    return _render(PORTAL_TITLE, rows)


def _render(title: str, rows: Sequence[tuple[bool, Task, str]]) -> Panel:
    if not rows:
        return layout.panel(Text(EMPTY_MESSAGE, style=theme.STYLE_HINT), title)

    table = layout.plain_table()
    table.add_column(no_wrap=True)
    table.add_column(justify="right", no_wrap=True)
    table.add_column(overflow="fold")
    table.add_column(no_wrap=True, style=theme.STYLE_HINT)

    for is_sent, task, reason in rows:
        table.add_row(
            _render_mark(is_sent),
            formatting.format_clock_time(task.logged_rounded),
            task.summary,
            task.project.name,
        )

        if reason:
            table.add_row("", "", Text(reason, style=theme.STYLE_HINT), "")

    return layout.panel(table, title)


def _render_mark(is_sent: bool) -> Text:
    if is_sent:
        return Text(theme.MARK_SENT, style=theme.STYLE_SUCCESS)

    return Text(theme.MARK_FAILED, style=theme.STYLE_FAILURE)
