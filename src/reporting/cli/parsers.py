import datetime

import dateutil.parser
import typer

LAST_REPORT_KEYWORD = "last"


def parse_report_date(value: str) -> datetime.date | None:
    if value == LAST_REPORT_KEYWORD:
        return None

    try:
        return dateutil.parser.parse(value, dayfirst=True).date()
    except (dateutil.parser.ParserError, OverflowError) as error:
        raise typer.BadParameter(f'"{value}" is not a date (DD.MM.YYYY) or "{LAST_REPORT_KEYWORD}"') from error
