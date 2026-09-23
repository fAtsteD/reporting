import datetime

import pytest
import typer

from reporting.cli import parsers


def test_reads_a_date_written_day_first() -> None:
    assert parsers.parse_report_date("20.08.2026") == datetime.date(2026, 8, 20)


def test_reads_no_date_for_the_last_report_keyword() -> None:
    assert parsers.parse_report_date("last") is None


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("bogus", id="not a date at all"),
        pytest.param("32.08.2026", id="a day that does not exist"),
    ],
)
def test_rejects_a_value_that_is_not_a_date(value: str) -> None:
    with pytest.raises(typer.BadParameter, match='is not a date \\(DD.MM.YYYY\\) or "last"'):
        parsers.parse_report_date(value)
