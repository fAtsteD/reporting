import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.orm import Session

from reporting import config
from reporting.database.models import Project
from tests.factories import KindFactory, ReportFactory, TaskFactory


def test_datetime_fields_round_trip_as_utc(database_session: Session) -> None:
    user_datetime = datetime.datetime(2026, 7, 1, 12, 0, tzinfo=ZoneInfo("Europe/Kyiv"))
    project = Project(alias="project", created_at=user_datetime, name="Project", updated_at=user_datetime)
    database_session.add(project)
    database_session.commit()
    database_session.expire(project)

    assert project.created_at == datetime.datetime(2026, 7, 1, 9, 0, tzinfo=datetime.UTC)
    assert project.updated_at == datetime.datetime(2026, 7, 1, 9, 0, tzinfo=datetime.UTC)


def test_report_totals(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config.app, "minute_round_to", 15)
    report = ReportFactory.create(date=datetime.date(2000, 1, 1), tasks=[])
    kind = KindFactory.create(tasks=[])

    for logged_minutes in (30, 115, 60):
        TaskFactory.create(
            kind=kind,
            kinds_id=kind.id,
            logged_seconds=logged_minutes * 60,
            report=report,
            reports_id=report.id,
        )

    assert report.total_rounded_seconds == (30 + 120 + 60) * 60
    assert report.total_seconds == (30 + 115 + 60) * 60


def test_task_logged_rounded(monkeypatch: pytest.MonkeyPatch) -> None:
    minute_round_to = 15
    monkeypatch.setattr(config.app, "minute_round_to", minute_round_to)
    task = TaskFactory.create(logged_seconds=0)

    assert task.logged_rounded == 0

    task.logged_timedelta(datetime.timedelta(minutes=5))
    assert task.logged_rounded == minute_round_to * 60

    task.logged_timedelta(datetime.timedelta(minutes=15))
    assert task.logged_rounded == minute_round_to * 60

    task.logged_timedelta(datetime.timedelta(hours=1, minutes=40))
    assert task.logged_rounded == 2 * 60 * 60
