import pytest

from reporting.services.jira import convert_time_to_jira_time


@pytest.mark.parametrize(
    "seconds, jira_str",
    [
        ((3 * 60 * 60 + 45 * 60), "3h 45m"),
        ((1 * 60 * 60), "1h 0m"),
        ((36 * 60), "0h 36m"),
        ((23 * 60 + 45), "0h 24m"),
        ((54 * 60 + 13), "0h 54m"),
    ],
    ids=[
        "hours and minutes",
        "strict hours",
        "strict minutes",
        "round minutes up",
        "round minutes down",
    ],
)
def test_convert_time_to_jira_time(seconds: int, jira_str: str) -> None:
    assert convert_time_to_jira_time(seconds) == jira_str
