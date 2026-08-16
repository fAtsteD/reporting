import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from reporting import config
from reporting.database.models import Kind, Project
from tests.factories import KindFactory, ProjectFactory, ReportFactory, TaskFactory


def test_kind_str() -> None:
    alias = "tk"
    name = "Test Kind"
    kind = Kind(alias=alias, name=name)
    assert str(kind) == f"{alias} - {name}"


def test_project_str() -> None:
    alias = "tp"
    name = "Test Project"
    kind = Project(alias=alias, name=name)
    assert str(kind) == f"{alias} - {name}"


def test_datetime_fields_round_trip_as_utc(database_session: Session) -> None:
    user_datetime = datetime.datetime(2026, 7, 1, 12, 0, tzinfo=ZoneInfo("Europe/Kyiv"))
    project = Project(alias="project", created_at=user_datetime, name="Project", updated_at=user_datetime)
    database_session.add(project)
    database_session.commit()
    database_session.expire(project)

    assert project.created_at == datetime.datetime(2026, 7, 1, 9, 0, tzinfo=datetime.UTC)
    assert project.updated_at == datetime.datetime(2026, 7, 1, 9, 0, tzinfo=datetime.UTC)


def test_report_properties() -> None:
    config.app.minute_round_to = 15
    report_date = datetime.date(2000, 1, 1)
    report_date_str = report_date.strftime("%d.%m.%Y")
    report = ReportFactory.create(date=report_date, tasks=[])
    kind = KindFactory.create(tasks=[])
    tasks = [
        TaskFactory.create(
            kind=kind,
            kinds_id=kind.id,
            logged_seconds=30 * 60,
            report=report,
            reports_id=report.id,
        ),
        TaskFactory.create(
            kind=kind,
            kinds_id=kind.id,
            logged_seconds=115 * 60,
            report=report,
            reports_id=report.id,
        ),
        TaskFactory.create(
            kind=kind,
            kinds_id=kind.id,
            logged_seconds=60 * 60,
            report=report,
            reports_id=report.id,
        ),
    ]
    tasks.sort(key=lambda task: task.summary)
    current_date_str = datetime.datetime.now(datetime.UTC).strftime("%d.%m.%Y")
    output_tasks = f"  {kind.name}:\n"

    for task in tasks:
        output_tasks += f"    {task}\n"

    assert report.total_rounded_seconds == (30 + 120 + 60) * 60
    assert report.total_seconds == (30 + 115 + 60) * 60
    assert str(report) == f"{report_date_str} ({current_date_str})\nSummary time: 03:30\nTasks:\n{output_tasks}"

    report.remove_tasks()
    assert report.total_rounded_seconds == 0
    assert report.total_seconds == 0
    assert str(report) == f"{report_date_str} ({current_date_str})\nSummary time: 00:00\nReport does not have tasks\n"


def test_task_properties() -> None:
    minute_round_to = 15
    config.app.minute_round_to = minute_round_to
    project = ProjectFactory.create(
        tasks=[],
    )
    task = TaskFactory.create(
        logged_seconds=0,
        project=project,
        projects_id=project.id,
    )

    assert task.logged_rounded == 0
    assert str(task) == f"00:00 - {task.summary} - {project.name}"

    task.logged_timedelta(datetime.timedelta(minutes=5))
    assert task.logged_rounded == minute_round_to * 60
    assert str(task) == f"00:{minute_round_to} - {task.summary} - {project.name}"

    task.logged_timedelta(datetime.timedelta(minutes=15))
    assert task.logged_rounded == minute_round_to * 60
    assert str(task) == f"00:{minute_round_to} - {task.summary} - {project.name}"

    task.logged_timedelta(datetime.timedelta(hours=1, minutes=40))
    assert task.logged_rounded == 2 * 60 * 60
    assert str(task) == f"02:00 - {task.summary} - {project.name}"
