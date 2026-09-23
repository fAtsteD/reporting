import datetime

import pytest

from reporting.cli.views import formatting


@pytest.mark.parametrize(
    "seconds, clock",
    [
        pytest.param(0, "00:00", id="no time"),
        pytest.param(30 * 60, "00:30", id="minutes only"),
        pytest.param(3 * 60 * 60 + 30 * 60, "03:30", id="hours are padded"),
        pytest.param(9 * 60 * 60 + 5 * 60, "09:05", id="hours and minutes are padded"),
        pytest.param(10 * 60 * 60 + 5 * 60, "10:05", id="minutes are padded"),
        pytest.param(100 * 60 * 60, "100:00", id="three digit hours"),
    ],
)
def test_pads_the_clock_to_two_digits(clock: str, seconds: int) -> None:
    assert formatting.format_clock_time(seconds) == clock


def test_writes_a_date_day_first() -> None:
    assert formatting.format_date(datetime.date(2026, 8, 20)) == "20.08.2026"
