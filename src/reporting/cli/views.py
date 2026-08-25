import datetime
from collections.abc import Sequence
from pathlib import Path

from reporting.database.models import Kind, Project, Report, Task
from reporting.services.jira.models import JiraTaskResult, JiraTaskStatus
from reporting.services.qatestlab_portal.models import PortalTaskResult, PortalTaskStatus

CONFIG_DESCRIPTION_INDENT = "    "
CONFIG_MISSING_FILE_NOTE = "(does not exist, every value is a default)"
DATE_FORMAT = "%d.%m.%Y"
FAILED_MARK = "[-]"
JIRA_TITLE = "Jira"
PORTAL_TITLE = "QATestLab Portal"
REPORT_CHANGED_MESSAGE = "Report changed, nothing was sent"
REPORT_NOT_FOUND_MESSAGE = "Report does not exist"
REPORT_WITHOUT_TASKS_MESSAGE = "Report does not have tasks"
SENT_MARK = "[+]"


def format_clock_time(seconds: int) -> str:
    hours = round(seconds / 60 // 60)
    minutes = round(seconds / 60 % 60)
    return f"{hours:02d}:{minutes:02d}"


def render_config_file_path(config_file_path: Path, is_existing: bool) -> str:
    if is_existing:
        return f"Config file: {config_file_path}"

    return f"Config file: {config_file_path} {CONFIG_MISSING_FILE_NOTE}"


def render_config_values(values: Sequence[tuple[str, str, str]]) -> str:
    key_width = max((len(key) for key, _, _ in values), default=0)
    lines = []

    for key, value, description in values:
        lines.append(f"{key.ljust(key_width)}  {value}")

        if description:
            lines.append(f"{CONFIG_DESCRIPTION_INDENT}{description}")

    return "\n".join(lines)


def render_date_mismatch(report_date: datetime.date, current_date: datetime.date) -> str:
    return f"Report date: {report_date.strftime(DATE_FORMAT)}\nCurrent date: {current_date.strftime(DATE_FORMAT)}"


def render_error(error: Exception) -> str:
    return f"Error: {error}"


def render_failure_count(failure_count: int) -> str:
    return f"Failed tasks: {failure_count}"


def render_jira_results(results: Sequence[JiraTaskResult]) -> str:
    lines = []

    for result in results:
        mark = SENT_MARK if result.status is JiraTaskStatus.SENT else FAILED_MARK
        lines.append(f"{mark} {render_task(result.task)}")

        if result.reason:
            lines.append(f"  {result.reason}")

    lines.append("")

    return "\n".join(lines)


def render_kind(kind: Kind) -> str:
    return f"{kind.alias} - {kind.name}"


def render_kinds(kinds: Sequence[Kind]) -> str:
    lines = ["Kinds:"]
    lines.extend(render_kind(kind) for kind in kinds)
    return "\n".join(lines)


def render_portal_results(results: Sequence[PortalTaskResult]) -> str:
    lines = []

    for result in results:
        mark = SENT_MARK if result.status is PortalTaskStatus.SENT else FAILED_MARK
        lines.append(f"{mark} {render_task(result.task)}")

        if result.reason:
            lines.append(f"  {result.reason}")

    return "\n".join(lines)


def render_project(project: Project) -> str:
    return f"{project.alias} - {project.name}"


def render_projects(projects: Sequence[Project]) -> str:
    lines = ["Projects:"]
    lines.extend(render_project(project) for project in projects)
    return "\n".join(lines)


def render_report(report: Report, current_date: datetime.date) -> str:
    lines = [
        f"{report.date.strftime(DATE_FORMAT)} ({current_date.strftime(DATE_FORMAT)})",
        f"Summary time: {format_clock_time(report.total_rounded_seconds)}",
    ]
    tasks = sorted(report.tasks, key=lambda task: (task.kind.name, task.summary))

    if not tasks:
        lines.append(REPORT_WITHOUT_TASKS_MESSAGE)
        return "\n".join(lines)

    lines.append("Tasks:")
    previous_kind = ""

    for task in tasks:
        if task.kind.name != previous_kind:
            lines.append(f"  {task.kind.name}:")

        lines.append(f"    {render_task(task)}")
        previous_kind = task.kind.name

    return "\n".join(lines)


def render_task(task: Task) -> str:
    return f"{format_clock_time(task.logged_rounded)} - {task.summary} - {task.project.name}"
