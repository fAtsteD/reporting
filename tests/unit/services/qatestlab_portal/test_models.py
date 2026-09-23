import pytest

from reporting.services.qatestlab_portal import qatestlab_portal_service
from reporting.services.qatestlab_portal.models import PortalMergedTask
from tests.factories.database import KindFactory, ProjectFactory, TaskFactory
from tests.fixtures.reporting_config import ReportingConfigFixture

_HOUR_SECONDS = 60 * 60


@pytest.mark.parametrize(
    "seconds, portal_hours",
    [
        pytest.param(0, 0, id="no time"),
        pytest.param(60 * 60, 100, id="one hour"),
        pytest.param(30 * 60, 50, id="half an hour"),
        pytest.param(90 * 60, 150, id="an hour and a half"),
        pytest.param(20 * 60, 33, id="a third of an hour is rounded"),
    ],
)
def test_converts_seconds_to_portal_hundredths_of_an_hour(portal_hours: int, seconds: int) -> None:
    assert qatestlab_portal_service.convert_seconds_to_portal_hours(seconds) == portal_hours


def test_names_a_project_a_merged_task_touches_twice_only_once() -> None:
    assert _build_merged_task(["My Project", "My Project"]).project_names == "My Project"


def test_names_every_project_a_merged_task_touches() -> None:
    assert _build_merged_task(["My Project", "Other Project"]).project_names == "My Project, Other Project"


def test_names_the_only_project_of_a_merged_task() -> None:
    assert _build_merged_task(["My Project"]).project_names == "My Project"


def test_sums_the_rounded_time_of_every_task_it_merges(reporting_config: ReportingConfigFixture) -> None:
    reporting_config({"app": {"minute-round-to": 0}})

    assert _build_merged_task(["My Project", "Other Project"]).logged_rounded == 2 * _HOUR_SECONDS


def _build_merged_task(project_names: list[str]) -> PortalMergedTask:
    tasks = tuple(
        TaskFactory.build(
            kind=KindFactory.build(),
            logged_seconds=_HOUR_SECONDS,
            project=ProjectFactory.build(name=project_name),
            summary="TEST-1: a task",
        )
        for project_name in project_names
    )

    return PortalMergedTask(description="TEST-1: a task", key="TEST-1", tasks=tasks, texts=("a task",))
