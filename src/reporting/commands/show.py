import datetime

import dateutil.parser
import sqlalchemy as sa
import typer

from reporting import config
from reporting.database import db_connection
from reporting.database.models import Report


def show(
    date: str = typer.Argument("last", help="Date to show (DD.MM.YYYY) or 'last'"),
) -> None:
    """Print report for date."""
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

        if report is None:
            print("Report does not exist")
        else:
            print(report)
