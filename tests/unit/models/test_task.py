import datetime

import faker
from sqlalchemy.orm import Session

from reporting.models.kind import Kind
from reporting.models.project import Project
from reporting.models.task import Task
from tests.conftest import ReportFixture, ReportingConfigFixture


def test_task_properties(
    reporting_config: ReportingConfigFixture,
    database_session: Session,
    get_report: ReportFixture,
    faker: faker.Faker,
) -> None:
    minute_round_to = 15
    reporting_config(
        {
            "minute-round-to": minute_round_to,
        }
    )
    report = get_report()
    kind = Kind(alias=faker.word(), name=faker.name())
    project = Project(alias=faker.word(), name=faker.name())
    task = Task(kind=kind, project=project, report=report, summary=faker.sentence())
    database_session.add_all([kind, project, task])
    database_session.commit()

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
