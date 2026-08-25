import datetime

import typer

from reporting import config
from reporting.cli import views
from reporting.database import db_connection
from reporting.services.file_parse import file_parse_service

PRINT_REPORTS_LIMIT = 10


def parse(
    days: int = typer.Argument(1, help="Number of days to parse, 0 for all"),
) -> None:
    current_date = datetime.datetime.now(config.app.timezone).date()

    with db_connection.session_scope() as session:
        reports = file_parse_service.parse_reports(session, days)
        print(f"Parsed {len(reports)}")

        if len(reports) < PRINT_REPORTS_LIMIT:
            for report in reports:
                print(views.render_report(report, current_date))
