import datetime

import typer

from reporting import config
from reporting.cli import parsers, views
from reporting.database import db_connection
from reporting.database.models import Report
from reporting.services.jira import jira_service
from reporting.services.jira.models import JiraTaskStatus
from reporting.services.qatestlab_portal import qatestlab_portal_service
from reporting.services.qatestlab_portal.models import PortalTaskStatus
from reporting.services.report import report_service

CONFIRM_ANSWER = "y"
SEND_QUESTION = "You try to send report not today. Do you want send report? (y/n) "


def send(
    date: str = typer.Argument(parsers.LAST_REPORT_KEYWORD, help="Date to send (DD.MM.YYYY) or 'last'"),
    to_jira: bool = typer.Option(False, "--jira", help="Send report to Jira"),
    to_portal: bool = typer.Option(False, "--portal", help="Send report to portal"),
) -> None:
    if not to_jira and not to_portal:
        typer.echo("Specify at least one target: --jira or --portal", err=True)
        raise typer.Exit(code=1)

    requested_date = parsers.parse_report_date(date)

    with db_connection.session_scope() as session:
        report = report_service.find_by_date_or_last(session, requested_date)
        report_id = None if report is None else report.id
        report_date = None if report is None else report.date

    if report_id is None or report_date is None:
        typer.echo(views.REPORT_NOT_FOUND_MESSAGE, err=True)
        raise typer.Exit(code=1)

    if not _confirm(report_date):
        return

    with db_connection.session_scope() as session:
        confirmed_report = report_service.find_by_id(session, report_id)

        if confirmed_report is None or confirmed_report.date != report_date:
            typer.echo(views.REPORT_CHANGED_MESSAGE, err=True)
            raise typer.Exit(code=1)

        failure_count = 0

        if to_jira:
            failure_count += _send_to_jira(confirmed_report)

        if to_portal:
            failure_count += _send_to_portal(confirmed_report)

    if failure_count:
        typer.echo(views.render_failure_count(failure_count), err=True)
        raise typer.Exit(code=1)


def _confirm(report_date: datetime.date) -> bool:
    current_date = datetime.datetime.now(config.app.timezone).date()

    if report_date == current_date:
        return True

    print(views.render_date_mismatch(report_date, current_date))

    return input(SEND_QUESTION) == CONFIRM_ANSWER


def _send_to_jira(report: Report) -> int:
    print(views.JIRA_TITLE)
    results = jira_service.set_worklog(report)
    print(views.render_jira_results(results))

    return len([result for result in results if result.status is JiraTaskStatus.FAILED])


def _send_to_portal(report: Report) -> int:
    print(views.PORTAL_TITLE)
    results = qatestlab_portal_service.send_tasks(report)
    rendered = views.render_portal_results(results)

    if rendered:
        print(rendered)

    return len([result for result in results if result.status is PortalTaskStatus.FAILED])
