import datetime

import faker
from sqlalchemy.orm import Session

from reporting.models.report import Report
from tests.conftest import ReportingConfigFixture, TaskFixture


def test_report_properties(
    reporting_config: ReportingConfigFixture,
    database_session: Session,
    add_task: TaskFixture,
    faker: faker.Faker,
) -> None:
    minute_round_to = 15
    reporting_config(
        {
            "minute-round-to": minute_round_to,
        }
    )
    report = Report(date=datetime.date(2000, 1, 1))
    database_session.add(report)
    tasks = [
        add_task(logged_seconds=30 * 60),
        add_task(logged_seconds=115 * 60),  # has to be rounded to 120
        add_task(logged_seconds=60 * 60),
    ]
    current_date_str = datetime.date.today().strftime("%d.%m.%Y")
    output_tasks = f"  {tasks[0].kind.name}:\n"

    for task in tasks:
        report.tasks.append(task)
        output_tasks += f"    {task}\n"
        database_session.add(task)

    database_session.commit()

    assert report.total_seconds == (30 + 120 + 60) * 60
    assert str(report) == f"01.01.2000 ({current_date_str})\nSummary time: 03:30\nTasks:\n{output_tasks}"

    report.remove_tasks()
    assert report.total_seconds == 0
    assert str(report) == f"01.01.2000 ({current_date_str})\nSummary time: 00:00\nReport does not have tasks\n"
