import datetime

from reporting import config_app
from reporting.models.project import Project
from reporting.models.task import Task
from tests.factories import ProjectFactory, TaskFactory


def test_task_properties() -> None:
    minute_round_to = 15
    config_app.config.minute_round_to = minute_round_to
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
