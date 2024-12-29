import datetime

from reporting import config
from reporting.models import Kind, Project, Report, Task
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


def test_report_properties() -> None:
    config.app.minute_round_to = 15
    report_date = datetime.date(2000, 1, 1)
    report_date_str = report_date.strftime("%d.%m.%Y")
    report: Report = ReportFactory.create(date=report_date, tasks=[])
    kind: Kind = KindFactory.create(tasks=[])
    tasks: list[Task] = [
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
    current_date_str = datetime.date.today().strftime("%d.%m.%Y")
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
    project: Project = ProjectFactory.create(
        tasks=[],
    )
    task: Task = TaskFactory.create(
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
