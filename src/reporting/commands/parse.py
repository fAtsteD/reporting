import typer

from reporting import config
from reporting.services.file_parse import file_parse_service


def parse(
    days: int = typer.Argument(1, help="Number of days to parse, 0 for all"),
) -> None:
    """Parse days from file and save to database."""
    config.load_config()
    reports = file_parse_service.parse_reports(days)
    print(f"Parsed {len(reports)}")

    if len(reports) < 10:
        for report in reports:
            print(report)
