import datetime

import dateutil.parser
import sqlalchemy as sa
import typer

from reporting import config
from reporting.database import db_connection
from reporting.database.models import Report
from reporting.services.jira import jira_service
from reporting.services.qatestlab_portal import qatestlab_portal_service


def send(
    date: str = typer.Argument("last", help="Date to send (DD.MM.YYYY) or 'last'"),
    to_jira: bool = typer.Option(False, "--jira", help="Send report to Jira"),
    to_portal: bool = typer.Option(False, "--portal", help="Send report to portal"),
) -> None:
    """Send report to selected systems."""
    if not to_jira and not to_portal:
        typer.echo("Specify at least one target: --jira or --portal")
        raise typer.Exit(code=1)

    config.load_config()
    report_date: str | datetime.date = date

    if date != "last":
        report_date = dateutil.parser.parse(date, dayfirst=True).date()

    with db_connection.session_scope() as session:
        report: Report | None

        if report_date == "last":
            report = session.scalars(sa.select(Report).order_by(Report.date.desc())).first()
        else:
            report = session.scalars(sa.select(Report).where(Report.date == report_date)).first()

        if to_jira:
            _send_to_jira(report)

        if to_portal:
            _send_to_portal(report)


def _send_to_jira(report: Report | None) -> None:
    current_date = datetime.datetime.now(config.app.timezone).date()
    jira_set_worklog = "y"
    print("Jira")

    if report:
        if report.date != current_date:
            print(f"Report date: {report.date.strftime('%d.%m.%Y')}\nCurrent date: {current_date.strftime('%d.%m.%Y')}")
            jira_set_worklog = input("You try to send report not today. Do you want set worklog? (y/n) ")

        if jira_set_worklog == "y":
            jira_service.set_worklog(report)


def _send_to_portal(report: Report | None) -> None:
    current_date = datetime.datetime.now(config.app.timezone).date()
    portal_send_task = "y"
    print("QATestLab Portal")

    if report:
        if report.date != current_date:
            print(f"Report date: {report.date.strftime('%d.%m.%Y')}\nCurrent date: {current_date.strftime('%d.%m.%Y')}")
            portal_send_task = input("You try to send report not today. Do you want send tasks? (y/n) ")

        if portal_send_task == "y":
            qatestlab_portal_service.send_tasks(report)
