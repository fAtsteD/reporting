import pytest

from reporting.services.jira import jira_service


@pytest.mark.parametrize(
    "seconds, jira_time",
    [
        pytest.param(3 * 60 * 60 + 45 * 60, "3h 45m", id="hours and minutes"),
        pytest.param(1 * 60 * 60, "1h 0m", id="whole hours"),
        pytest.param(36 * 60, "0h 36m", id="whole minutes"),
        pytest.param(23 * 60 + 45, "0h 24m", id="seconds round minutes up"),
        pytest.param(54 * 60 + 13, "0h 54m", id="seconds round minutes down"),
        pytest.param(59 * 60 + 45, "1h 0m", id="minutes rounded up to a full hour"),
        pytest.param(1 * 60 * 60 + 59 * 60 + 30, "2h 0m", id="minutes rounded up to the next hour"),
    ],
)
def test_converts_seconds_to_jira_hours_and_rounded_minutes(seconds: int, jira_time: str) -> None:
    assert jira_service.convert_time_to_jira_time(seconds) == jira_time
