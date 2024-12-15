import faker
import pytest
from sqlalchemy.orm import Session

from reporting import cli
from reporting.models.project import Project
from tests.conftest import ReportingConfigFixture
from tests.factories import ProjectFactory


def test_add_project(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    project_raw = {
        "alias": "wide-eyed-tip",
        "name": "Product Mobility Consultant",
    }
    output_expected = "Projects:\n"
    output_expected += f"{project_raw['alias']} - {project_raw['name']}\n"

    cli.main(["--project", project_raw["alias"], project_raw["name"]])

    output = capsys.readouterr()
    assert output.out == (output_expected)

    saved_project = database_session.query(Project).first()
    assert saved_project is not None
    assert saved_project.alias == project_raw["alias"]
    assert saved_project.name == project_raw["name"]


def test_show_projects(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    projects: list[Project] = [
        ProjectFactory.create(tasks=[]),
        ProjectFactory.create(tasks=[]),
        ProjectFactory.create(tasks=[]),
    ]
    projects.sort(key=lambda project: project.name)
    output_expected = "Projects:\n"

    for project in projects:
        output_expected += f"{project}\n"

    cli.main(["--show-projects"])

    output = capsys.readouterr()
    assert output.out == (output_expected)


def test_show_projects_empty(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    output_expected = "Projects:\n"

    cli.main(["--show-projects"])

    output = capsys.readouterr()
    assert output.out == (output_expected)


def test_update_project(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    faker: faker.Faker,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    project: Project = ProjectFactory.create(tasks=[])
    project_new_name = faker.sentence(nb_words=3, variable_nb_words=True)
    output_expected = "Projects:\n"
    output_expected += f"{project.alias} - {project_new_name}\n"

    cli.main(["--project", project.alias, project_new_name])

    output = capsys.readouterr()
    assert output.out == (output_expected)

    saved_project = database_session.query(Project).first()
    assert saved_project is not None
    assert saved_project.alias == project.alias
    assert saved_project.name == project_new_name
