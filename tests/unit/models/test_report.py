import datetime

from reporting import config_app
from reporting.models.kind import Kind
from reporting.models.report import Report
from reporting.models.task import Task
from tests.factories import KindFactory, ReportFactory, TaskFactory


def test_report_properties() -> None:
    config_app.config.minute_round_to = 15
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
