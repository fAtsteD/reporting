import datetime

import pytest

from reporting import config
from reporting.config.app import AppConfig
from reporting.services.file_parse import TaskLine, parse_task

REPORT_DATE = datetime.date(2026, 8, 2)


@pytest.mark.parametrize(
    "line, expected",
    [
        (
            "09 00",
            TaskLine(
                kind=AppConfig.default_kind,
                project=AppConfig.default_project,
                time_begin=datetime.datetime.combine(REPORT_DATE, datetime.time(9, 0)),
            ),
        ),
        (
            "09 10 - Harum beatae\\-molestiae.",
            TaskLine(
                kind=AppConfig.default_kind,
                project=AppConfig.default_project,
                summary="Harum beatae-molestiae.",
                time_begin=datetime.datetime.combine(REPORT_DATE, datetime.time(9, 10)),
            ),
        ),
        (
            "09 10 - inventore \\- modi quia",
            TaskLine(
                kind=AppConfig.default_kind,
                project=AppConfig.default_project,
                summary="inventore - modi quia",
                time_begin=datetime.datetime.combine(REPORT_DATE, datetime.time(9, 10)),
            ),
        ),
        (
            "10 30 - Non hic repellendus facere architecto reprehenderit aut dolore est quaerat.",
            TaskLine(
                kind=AppConfig.default_kind,
                project=AppConfig.default_project,
                summary="Non hic repellendus facere architecto reprehenderit aut dolore est quaerat.",
                time_begin=datetime.datetime.combine(REPORT_DATE, datetime.time(10, 30)),
            ),
        ),
        (
            "11 45 - Incidunt non omnis ut porro ut nostrum. - eum",
            TaskLine(
                kind="eum",
                project=AppConfig.default_project,
                summary="Incidunt non omnis ut porro ut nostrum.",
                time_begin=datetime.datetime.combine(REPORT_DATE, datetime.time(11, 45)),
            ),
        ),
        (
            "12 00 - debitis autem ipsa - quasi - Dynamic Response Associate",
            TaskLine(
                kind="quasi",
                project="Dynamic Response Associate",
                summary="debitis autem ipsa",
                time_begin=datetime.datetime.combine(REPORT_DATE, datetime.time(12, 0)),
            ),
        ),
    ],
    ids=[
        "only time",
        "time, summary escaped",
        "time, summary escaped with spaces",
        "time, summary",
        "time, summary, kind",
        "time, summary, kind, project",
    ],
)
def test_parse_line(monkeypatch: pytest.MonkeyPatch, line: str, expected: TaskLine) -> None:
    monkeypatch.setattr(config, "app", AppConfig(timezone_name="Europe/Kyiv"))
    task_line = parse_task(line, REPORT_DATE)
    expected.time_begin = expected.time_begin.replace(tzinfo=config.app.timezone)
    assert task_line == expected
