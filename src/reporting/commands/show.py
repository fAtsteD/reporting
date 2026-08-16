import datetime

import dateutil.parser
import typer

from reporting import config
from reporting.database import db_connection
from reporting.database.models import Report


def show(
    date: str = typer.Argument("last", help="Date to show (DD.MM.YYYY) or 'last'"),
) -> None:
    """Print report for date."""
    config.load_config()
    report: Report | None = None
    report_date: str | datetime.date = date

    if date != "last":
        report_date = dateutil.parser.parse(date, dayfirst=True).date()

    if report_date == "last":
        report = db_connection.session.query(Report).order_by(Report.date.desc()).first()
    else:
        report = db_connection.session.query(Report).filter(Report.date == report_date).first()

    if report is None:
        print("Report does not exist")
    else:
        print(report)
