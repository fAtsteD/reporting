import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Task
from reporting.services.report import report_service
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory


def test_deleting_a_report_deletes_its_tasks(database_session: Session) -> None:
    report = ReportFactory.create(date=datetime.date(2026, 8, 20))
    TaskFactory.create(report=report, summary="only task")

    database_session.delete(report)
    database_session.commit()

    assert database_session.scalars(sa.select(Task)).all() == []


def test_finds_no_report_for_an_unknown_id(database_session: Session) -> None:
    report = ReportFactory.create(date=datetime.date(2026, 8, 18))

    assert report_service.find_by_id(database_session, report.id + 1000) is None


def test_finds_no_report_when_no_report_has_that_date(database_session: Session) -> None:
    ReportFactory.create(date=datetime.date(2026, 8, 18))

    assert report_service.find_by_date(database_session, datetime.date(2015, 1, 1)) is None


def test_finds_no_report_when_none_is_saved(database_session: Session) -> None:
    assert report_service.find_last(database_session) is None


def test_finds_the_latest_report_when_no_date_is_given(database_session: Session) -> None:
    ReportFactory.create(date=datetime.date(2026, 8, 18))
    latest = ReportFactory.create(date=datetime.date(2026, 8, 20))
    ReportFactory.create(date=datetime.date(2026, 8, 19))

    found = report_service.find_by_date_or_last(database_session, None)

    assert found is not None
    assert found.id == latest.id


def test_finds_the_report_by_its_id(database_session: Session) -> None:
    ReportFactory.create(date=datetime.date(2026, 8, 18))
    wanted = ReportFactory.create(date=datetime.date(2026, 8, 20))

    found = report_service.find_by_id(database_session, wanted.id)

    assert found is not None
    assert found.date == datetime.date(2026, 8, 20)


def test_finds_the_report_of_the_given_date(database_session: Session) -> None:
    ReportFactory.create(date=datetime.date(2026, 8, 18))
    wanted = ReportFactory.create(date=datetime.date(2026, 8, 19))
    ReportFactory.create(date=datetime.date(2026, 8, 20))

    found = report_service.find_by_date(database_session, datetime.date(2026, 8, 19))

    assert found is not None
    assert found.id == wanted.id


def test_finds_the_report_of_the_given_date_when_a_date_is_given(database_session: Session) -> None:
    wanted = ReportFactory.create(date=datetime.date(2026, 8, 18))
    ReportFactory.create(date=datetime.date(2026, 8, 20))

    found = report_service.find_by_date_or_last(database_session, datetime.date(2026, 8, 18))

    assert found is not None
    assert found.id == wanted.id


def test_loads_the_kind_and_project_of_every_task(database_session: Session) -> None:
    report = ReportFactory.create(date=datetime.date(2026, 8, 20))
    TaskFactory.create(
        kind=KindFactory.create(name="Develop"),
        project=ProjectFactory.create(name="My Project"),
        report=report,
        summary="only task",
    )
    database_session.expire_all()

    found = report_service.find_by_id(database_session, report.id)
    database_session.expunge_all()

    assert found is not None
    assert [(task.kind.name, task.project.name) for task in found.tasks] == [("Develop", "My Project")]
