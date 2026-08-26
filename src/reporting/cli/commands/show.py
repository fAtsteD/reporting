import datetime

import typer

from reporting import config
from reporting.cli import output, parsers
from reporting.cli.views import view_message, view_report
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
            output.print_result(view_report.render(report, current_date))
            return

    output.print_diagnostic(view_message.render_notice(view_message.REPORT_NOT_FOUND_MESSAGE))
    raise typer.Exit(code=1)
