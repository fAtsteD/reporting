import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Project
from tests.assertions import cli_output
from tests.factories.database import ProjectFactory
from tests.fixtures.cli import RunCli


def test_project_add_saves_the_project_and_prints_the_projects(
    database_session: Session,
    run_cli: RunCli,
) -> None:
    result = run_cli("project", "add", "mp", "My Project")

    cli_output.assert_lines(result.out, ["Projects", "mp My Project"])
    saved_project = database_session.scalars(sa.select(Project)).one()
    assert (saved_project.alias, saved_project.name) == ("mp", "My Project")


def test_project_list_prints_the_stored_projects(
    run_cli: RunCli,
) -> None:
    ProjectFactory.create(alias="p1", name="Alpha")
    ProjectFactory.create(alias="p2", name="Beta")

    result = run_cli("project", "list")

    cli_output.assert_lines(result.out, ["Projects", "p1 Alpha", "p2 Beta"])
