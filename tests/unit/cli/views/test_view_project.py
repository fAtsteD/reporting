from reporting.cli.views import view_project
from tests.assertions import cli_output
from tests.factories.database import ProjectFactory


def test_renders_a_note_when_there_are_no_projects() -> None:
    output = cli_output.render(view_project.render([]))

    cli_output.assert_lines(output, ["Projects", "No projects yet"])


def test_renders_one_row_per_project() -> None:
    projects = [ProjectFactory.build(alias="p1", name="Alpha"), ProjectFactory.build(alias="p2", name="Beta")]

    output = cli_output.render(view_project.render(projects))

    cli_output.assert_lines(output, ["Projects", "p1 Alpha", "p2 Beta"])
