import datetime

import typer

from reporting import config
from reporting.cli import output, parsers
from reporting.cli.views import view_message, view_send
from reporting.database import db_connection
from reporting.database.models import Report
from reporting.services.jira import jira_service
from reporting.services.jira.models import JiraTaskStatus
from reporting.services.qatestlab_portal import qatestlab_portal_service
from reporting.services.qatestlab_portal.models import PortalTaskStatus
from reporting.services.report import report_service


def send(
    date: str = typer.Argument(parsers.LAST_REPORT_KEYWORD, help="Date to send (DD.MM.YYYY) or 'last'"),
    to_jira: bool = typer.Option(False, "--jira", help="Send report to Jira"),
    to_portal: bool = typer.Option(False, "--portal", help="Send report to portal"),
) -> None:
    if not to_jira and not to_portal:
        output.print_diagnostic(view_message.render_notice(view_message.NO_TARGET_MESSAGE))
        raise typer.Exit(code=1)

    requested_date = parsers.parse_report_date(date)

    with db_connection.session_scope() as session:
        report = report_service.find_by_date_or_last(session, requested_date)
        report_id = None if report is None else report.id
        report_date = None if report is None else report.date

    if report_id is None or report_date is None:
        output.print_diagnostic(view_message.render_notice(view_message.REPORT_NOT_FOUND_MESSAGE))
        raise typer.Exit(code=1)

    if not _confirm(report_date):
        return

    with db_connection.session_scope() as session:
        confirmed_report = report_service.find_by_id(session, report_id)

        if confirmed_report is None or confirmed_report.date != report_date:
            output.print_diagnostic(view_message.render_notice(view_message.REPORT_CHANGED_MESSAGE))
            raise typer.Exit(code=1)

        failure_count = 0

        if to_jira:
            failure_count += _send_to_jira(confirmed_report)

        if to_portal:
            failure_count += _send_to_portal(confirmed_report)

    if failure_count:
        output.print_diagnostic(view_message.render_failure_count(failure_count))
        raise typer.Exit(code=1)


def _confirm(report_date: datetime.date) -> bool:
    current_date = datetime.datetime.now(config.app.timezone).date()

    if report_date == current_date:
        return True

    output.print_result(view_send.render_date_mismatch(report_date, current_date))

    return output.confirm(view_message.SEND_QUESTION)


def _send_to_jira(report: Report) -> int:
    output.print_progress(view_send.JIRA_PROGRESS_MESSAGE)
    results = jira_service.set_worklog(report)
    output.print_result(view_send.render_jira_results(results))

    return sum(len(result.merged_task.tasks) for result in results if result.status is JiraTaskStatus.FAILED)


def _send_to_portal(report: Report) -> int:
    output.print_progress(view_send.PORTAL_PROGRESS_MESSAGE)
    results = qatestlab_portal_service.send_tasks(report)
    output.print_result(view_send.render_portal_results(results))

    return sum(len(result.merged_task.tasks) for result in results if result.status is PortalTaskStatus.FAILED)
