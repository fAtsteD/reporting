import datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Task
from reporting.services.file_parse import file_parse_service
from reporting.services.file_parse.exceptions import (
    FileParseError,
    FileParseNotConfiguredError,
    UnknownKindError,
    UnknownProjectError,
)
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.reporting_config import ReportingConfigFixture
from tests.fixtures.tracking_file import TrackingFileFixture

_MINUTE_SECONDS = 60
_REPORT_DATE = datetime.date(2026, 8, 20)


def test_assigns_the_default_kind_and_project_when_a_line_has_none(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    kind = KindFactory.create(alias="dev", name="Develop")
    project = ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - a task", "10 00 - another task"],
        app={"default-type": "dev", "default-project": "mp"},
    )

    file_parse_service.parse_reports(database_session)

    task = database_session.scalars(sa.select(Task).where(Task.summary == "a task")).one()
    assert (task.kinds_id, task.projects_id) == (kind.id, project.id)


def test_counts_an_omitted_task_as_time_of_the_task_above(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - a task - dev - mp", "10 00 - lunch - dev - mp", "10 30 - another - dev - mp"],
        app={"default-type": "dev", "default-project": "mp", "omit-task": ["lunch"]},
    )

    file_parse_service.parse_reports(database_session)

    assert _logged_minutes(database_session, "a task") == 60


def test_fails_on_an_unknown_kind_alias(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(reporting_config, tracking_file, ["20.08.2026", "09 00 - a task - dev - mp"])

    with pytest.raises(UnknownKindError, match='Kind dev does not exist. Add it: reporting kind add dev "<name>"'):
        file_parse_service.parse_reports(database_session)


def test_fails_on_an_unknown_project_alias(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    _configure(reporting_config, tracking_file, ["20.08.2026", "09 00 - a task - dev - mp"])

    with pytest.raises(UnknownProjectError, match="Project mp does not exist"):
        file_parse_service.parse_reports(database_session)


def test_fails_when_the_tracking_file_does_not_exist(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config({"app": {"hour-report-path": "/nowhere/tracking.txt"}})

    with pytest.raises(FileParseNotConfiguredError, match="does not exist"):
        file_parse_service.parse_reports(database_session)


def test_fails_when_the_tracking_file_is_not_configured(
    database_session: Session,
) -> None:
    with pytest.raises(FileParseNotConfiguredError, match="is not configured"):
        file_parse_service.parse_reports(database_session)


def test_fills_the_last_task_of_a_day_up_to_the_work_day_length(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - a task - dev - mp", "10 00 - last task - dev - mp", "", "", ""],
        app={"default-type": "dev", "default-project": "mp", "work-day-hours": 8.0},
    )

    file_parse_service.parse_reports(database_session)

    assert _logged_minutes(database_session, "last task") == 7 * 60


def test_imports_no_report_from_an_empty_file(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    _configure(reporting_config, tracking_file, [])

    assert file_parse_service.parse_reports(database_session) == []


def test_keeps_the_last_task_when_the_day_is_already_full(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - a task - dev - mp", "18 00 - last task - dev - mp", "", "", ""],
        app={"default-type": "dev", "default-project": "mp", "work-day-hours": 8.0},
    )

    file_parse_service.parse_reports(database_session)

    assert _logged_minutes(database_session, "last task") == 0


def test_merges_repeated_lines_of_the_same_task_kind_and_project(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        [
            "20.08.2026",
            "09 00 - a task - dev - mp",
            "10 00 - another task - dev - mp",
            "11 00 - a task - dev - mp",
            "11 30 - another task - dev - mp",
        ],
        app={"default-type": "dev", "default-project": "mp"},
    )

    file_parse_service.parse_reports(database_session)

    assert database_session.scalar(sa.select(sa.func.count()).select_from(Task)) == 2
    assert _logged_minutes(database_session, "a task") == 90


def test_omits_a_task_named_in_the_omit_list(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - a task - dev - mp", "10 00 - lunch - dev - mp", "10 30 - a task - dev - mp"],
        app={"default-type": "dev", "default-project": "mp", "omit-task": ["lunch"]},
    )

    file_parse_service.parse_reports(database_session)

    assert [task.summary for task in database_session.scalars(sa.select(Task))] == ["a task"]


def test_reads_every_day_when_days_is_zero(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        [
            "20.08.2026",
            "09 00 - first day task - dev - mp",
            "",
            "",
            "21.08.2026",
            "09 00 - second day task - dev - mp",
            "",
            "",
            "22.08.2026",
            "09 00 - third day task - dev - mp",
        ],
        app={"default-type": "dev", "default-project": "mp"},
    )

    reports = file_parse_service.parse_reports(database_session, read_days=0)

    assert [report.date for report in reports] == [
        datetime.date(2026, 8, 20),
        datetime.date(2026, 8, 21),
        datetime.date(2026, 8, 22),
    ]


def test_reads_only_the_requested_number_of_days(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        [
            "20.08.2026",
            "09 00 - first day task - dev - mp",
            "10 00 - first day end - dev - mp",
            "",
            "",
            "21.08.2026",
            "09 00 - second day task - dev - mp",
            "10 00 - second day end - dev - mp",
            "",
            "",
            "22.08.2026",
            "09 00 - third day task - dev - mp",
        ],
        app={"default-type": "dev", "default-project": "mp"},
    )

    reports = file_parse_service.parse_reports(database_session, read_days=2)

    assert [report.date for report in reports] == [datetime.date(2026, 8, 20), datetime.date(2026, 8, 21)]


def test_rejects_a_day_heading_that_is_not_a_date(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    _configure(reporting_config, tracking_file, ["45.45.2026", "09 00 - a task"])

    with pytest.raises(FileParseError, match="Line is not a date"):
        file_parse_service.parse_reports(database_session)


def test_rejects_a_task_line_that_does_not_start_with_a_time(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    _configure(reporting_config, tracking_file, ["20.08.2026", "not a time - a task"])

    with pytest.raises(FileParseError, match="Line does not start with a time"):
        file_parse_service.parse_reports(database_session)


def test_replaces_the_tasks_of_a_report_that_already_exists(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    existing_report = ReportFactory.create(date=_REPORT_DATE)
    TaskFactory.create_batch(6, report=existing_report)
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - a task - dev - mp", "10 00 - another task - dev - mp"],
        app={"default-type": "dev", "default-project": "mp"},
    )

    file_parse_service.parse_reports(database_session)

    assert sorted(task.summary for task in database_session.scalars(sa.select(Task))) == ["a task", "another task"]


def test_sums_the_time_between_consecutive_lines_into_the_task_above(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - first task - dev - mp", "10 30 - second task - dev - mp"],
        app={"default-type": "dev", "default-project": "mp"},
    )

    file_parse_service.parse_reports(database_session)

    assert _logged_minutes(database_session, "first task") == 90


def test_translates_a_short_task_name_through_the_dictionary(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    _configure(
        reporting_config,
        tracking_file,
        ["20.08.2026", "09 00 - l - dev - mp", "10 00 - a task - dev - mp"],
        app={"default-type": "dev", "default-project": "mp"},
        dictionary={"task": {"l": "lunch"}},
    )

    file_parse_service.parse_reports(database_session)

    assert "lunch" in [task.summary for task in database_session.scalars(sa.select(Task))]


def _configure(
    reporting_config: ReportingConfigFixture,
    tracking_file: TrackingFileFixture,
    lines: list[str],
    app: dict | None = None,
    dictionary: dict | None = None,
) -> None:
    reporting_config(
        {
            "app": {"hour-report-path": str(tracking_file(lines)), "timezone": "UTC"} | (app or {}),
            "dictionary": dictionary or {},
        }
    )


def _logged_minutes(session: Session, summary: str) -> int:
    task = session.scalars(sa.select(Task).where(Task.summary == summary)).one()

    return task.logged_seconds // _MINUTE_SECONDS
