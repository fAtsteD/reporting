import datetime

import typer

from reporting import config
from reporting.cli import parsers, views
from reporting.database import db_connection
from reporting.services.report import report_service


def show(
    date: str = typer.Argument(parsers.LAST_REPORT_KEYWORD, help="Date to show (DD.MM.YYYY) or 'last'"),
) -> None:
    current_date = datetime.datetime.now(config.app.timezone).date()
    report_date = parsers.parse_report_date(date)

    with db_connection.session_scope() as session:
        report = report_service.find_by_date_or_last(session, report_date)

        if report is not None:
            print(views.render_report(report, current_date))
            return

    typer.echo(views.REPORT_NOT_FOUND_MESSAGE, err=True)
    raise typer.Exit(code=1)
