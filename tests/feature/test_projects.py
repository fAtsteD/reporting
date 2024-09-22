import pytest
from sqlalchemy.orm import Session

from reporting import cli
from reporting.models.project import Project
from tests.conftest import ReportingConfigFixture


def test_add_project(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
    database_session: Session,
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
    database_session: Session,
) -> None:
    reporting_config()
    projects = [
        Project(alias="acrobatic-fourths", name="Dynamic Metrics Analyst"),
        Project(alias="uniform-chuck", name="International Operations Producer"),
        Project(alias="magnificent-membrane", name="Customer Directives Consultant"),
    ]
    output_expected = "Projects:\n"
    for project in projects:
        database_session.add(project)
        output_expected += f"{project}\n"
    database_session.commit()

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
    reporting_config: ReportingConfigFixture,
    database_session: Session,
) -> None:
    reporting_config()
    project_raw = {
        "alias": "these-presentation",
        "name": "Chief Accountability Liaison",
    }
    project_exist = Project(alias=project_raw["alias"], name="Chief Tactics Producer")
    database_session.add(project_exist)
    database_session.commit()
    output_expected = "Projects:\n"
    output_expected += f"{project_raw['alias']} - {project_raw['name']}\n"

    cli.main(["--project", project_raw["alias"], project_raw["name"]])
    output = capsys.readouterr()

    assert output.out == (output_expected)
    saved_project = database_session.query(Project).first()
    assert saved_project is not None
    assert saved_project.alias == project_raw["alias"]
    assert saved_project.name == project_raw["name"]
