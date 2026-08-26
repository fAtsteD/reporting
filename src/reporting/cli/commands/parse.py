import datetime

import typer

from reporting import config
from reporting.cli import output
from reporting.cli.views import view_message, view_report
from reporting.database import db_connection
from reporting.services.file_parse import file_parse_service

PRINT_REPORTS_LIMIT = 10


def parse(
    days: int = typer.Argument(1, help="Number of days to parse, 0 for all"),
) -> None:
    current_date = datetime.datetime.now(config.app.timezone).date()

    with db_connection.session_scope() as session:
        reports = file_parse_service.parse_reports(session, days)
        output.print_result(view_message.render_parsed_count(len(reports)))

        if len(reports) < PRINT_REPORTS_LIMIT:
            for report in reports:
                output.print_result(view_report.render(report, current_date))
