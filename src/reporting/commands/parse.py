import typer

from reporting import config
from reporting.database import db_connection
from reporting.services.file_parse import file_parse_service


def parse(
    days: int = typer.Argument(1, help="Number of days to parse, 0 for all"),
) -> None:
    """Parse days from file and save to database."""
    config.load_config()

    with db_connection.session_scope() as session:
        reports = file_parse_service.parse_reports(session, days)
        print(f"Parsed {len(reports)}")

        if len(reports) < 10:
            for report in reports:
                print(report)
