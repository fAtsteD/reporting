import datetime

import pytest

from reporting.database.models import Report, Task
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.reporting_config import ReportingConfigFixture

_MINUTE_SECONDS = 60


def test_adds_a_logged_period_to_the_time_already_logged() -> None:
    task = _build_task(30 * _MINUTE_SECONDS)

    task.logged_timedelta(datetime.timedelta(minutes=15))

    assert task.logged_seconds == 45 * _MINUTE_SECONDS


def test_keeps_the_exact_logged_time_when_rounding_is_disabled(
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config({"app": {"minute-round-to": 0}})

    assert _build_task(23 * _MINUTE_SECONDS).logged_rounded == 23 * _MINUTE_SECONDS


def test_report_total_rounded_seconds_sums_the_rounded_time_of_its_tasks(
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config({"app": {"minute-round-to": 15}})

    assert _build_report([30, 115, 60]).total_rounded_seconds == (30 + 120 + 60) * _MINUTE_SECONDS


def test_report_total_seconds_sums_the_logged_time_of_its_tasks(
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config({"app": {"minute-round-to": 15}})

    assert _build_report([30, 115, 60]).total_seconds == (30 + 115 + 60) * _MINUTE_SECONDS


@pytest.mark.parametrize(
    "logged_minutes, rounded_minutes",
    [
        pytest.param(0, 0, id="no logged time stays zero"),
        pytest.param(1, 15, id="less than half a step rounds up to one step"),
        pytest.param(5, 15, id="a few minutes round up to one step"),
        pytest.param(15, 15, id="an exact step is kept"),
        pytest.param(22, 15, id="below the half-up threshold rounds down"),
        pytest.param(23, 30, id="at the half-up threshold rounds up"),
        pytest.param(53, 60, id="rounding up carries into the hour"),
        pytest.param(100, 105, id="over an hour rounds within the hour"),
    ],
)
def test_rounds_the_logged_time_to_the_configured_minutes(
    logged_minutes: int,
    reporting_config: ReportingConfigFixture,
    rounded_minutes: int,
) -> None:
    reporting_config({"app": {"minute-round-to": 15}})

    assert _build_task(logged_minutes * _MINUTE_SECONDS).logged_rounded == rounded_minutes * _MINUTE_SECONDS


@pytest.mark.parametrize(
    "summary",
    [
        pytest.param("TEST-12345:", id="nothing after the double dots"),
        pytest.param("lunch: with a colleague", id="left part without a number"),
        pytest.param("some words 123: with a number", id="left part with a space"),
        pytest.param("without double dots", id="summary without double dots"),
        pytest.param("note: no digit in the key", id="left part without a digit"),
    ],
)
def test_task_keeps_a_summary_without_a_key_as_the_text(summary: str) -> None:
    task = Task(summary=summary)

    assert task.summary_key == ""
    assert task.summary_text == summary


@pytest.mark.parametrize(
    "summary, key, text",
    [
        pytest.param("TEST-12345: I have done something", "TEST-12345", "I have done something", id="key and text"),
        pytest.param("TEST-12345:I have done something", "TEST-12345", "I have done something", id="without a space"),
        pytest.param("0123456: Do something", "0123456", "Do something", id="key of numbers only"),
        pytest.param("TEST-12345:   ", "TEST-12345", "", id="text of spaces only"),
        pytest.param("TEST-1: a: b", "TEST-1", "a: b", id="another colon inside the text"),
    ],
)
def test_task_splits_a_summary_that_begins_with_a_key(summary: str, key: str, text: str) -> None:
    task = Task(summary=summary)

    assert task.summary_key == key
    assert task.summary_text == text


def _build_report(logged_minutes: list[int]) -> Report:
    report = ReportFactory.build()

    for minutes in logged_minutes:
        TaskFactory.build(
            kind=KindFactory.build(),
            logged_seconds=minutes * _MINUTE_SECONDS,
            project=ProjectFactory.build(),
            report=report,
        )

    return report


def _build_task(logged_seconds: int) -> Task:
    return TaskFactory.build(kind=KindFactory.build(), logged_seconds=logged_seconds, project=ProjectFactory.build())
