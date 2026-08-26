import datetime
from collections.abc import Sequence

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from reporting.cli.views import formatting, layout, theme
from reporting.database.models import Report, Task

SUBTITLE_SEPARATOR = " · "
TITLE_PREFIX = "Report "
WITHOUT_TASKS_MESSAGE = "Report does not have tasks"


def render(report: Report, current_date: datetime.date) -> Panel:
    title = f"{TITLE_PREFIX}{formatting.format_date(report.date)}"
    subtitle = (
        f"total {formatting.format_clock_time(report.total_rounded_seconds)}"
        f"{SUBTITLE_SEPARATOR}today {formatting.format_date(current_date)}"
    )
    tasks = sorted(report.tasks, key=lambda task: (task.kind.name, task.summary))

    if not tasks:
        return layout.panel(Text(WITHOUT_TASKS_MESSAGE, style=theme.STYLE_HINT), title, subtitle)

    return layout.panel(_render_tasks(tasks), title, subtitle)


def _render_tasks(tasks: Sequence[Task]) -> Table:
    table = layout.plain_table()
    table.add_column(justify="right", no_wrap=True)
    table.add_column(overflow="fold")
    table.add_column(no_wrap=True, style=theme.STYLE_HINT)
    previous_kind = ""

    for task in tasks:
        if task.kind.name != previous_kind:
            table.add_row("", Text(task.kind.name, style=theme.STYLE_KEY), "")

        table.add_row(formatting.format_clock_time(task.logged_rounded), task.summary, task.project.name)
        previous_kind = task.kind.name

    return table
