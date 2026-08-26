import datetime

DATE_FORMAT = "%d.%m.%Y"


def format_clock_time(seconds: int) -> str:
    hours = round(seconds / 60 // 60)
    minutes = round(seconds / 60 % 60)
    return f"{hours:02d}:{minutes:02d}"


def format_date(date: datetime.date) -> str:
    return date.strftime(DATE_FORMAT)
