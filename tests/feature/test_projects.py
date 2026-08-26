import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Project
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import ProjectFactory
from tests.fixtures.cli import RunCli


def test_add_project(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("project", "add", "wide-eyed-tip", "Product Mobility Consultant")

    assert rendered_output.cells(result.out) == [
        ["Projects"],
        ["wide-eyed-tip", "Product Mobility Consultant"],
    ]

    saved_project = database_session.scalars(sa.select(Project)).first()
    assert saved_project is not None
    assert saved_project.alias == "wide-eyed-tip"
    assert saved_project.name == "Product Mobility Consultant"


def test_show_projects(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    ProjectFactory.create(alias="p3", name="Gamma", tasks=[])
    ProjectFactory.create(alias="p1", name="Alpha", tasks=[])
    ProjectFactory.create(alias="p2", name="Beta", tasks=[])

    result = run_cli("project", "list")

    assert rendered_output.cells(result.out) == [
        ["Projects"],
        ["p1", "Alpha"],
        ["p2", "Beta"],
        ["p3", "Gamma"],
    ]


def test_show_projects_empty(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("project", "list")

    assert rendered_output.cells(result.out) == [["Projects"], ["No projects yet"]]


def test_update_project(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    ProjectFactory.create(alias="p1", name="Old Name", tasks=[])

    result = run_cli("project", "add", "p1", "New Name")
    database_session.expire_all()

    assert rendered_output.cells(result.out) == [["Projects"], ["p1", "New Name"]]

    saved_project = database_session.scalars(sa.select(Project)).first()
    assert saved_project is not None
    assert saved_project.alias == "p1"
    assert saved_project.name == "New Name"
