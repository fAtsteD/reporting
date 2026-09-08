import datetime

import faker
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Kind, Project, Report, Task
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import RunCli
from tests.fixtures.portal import PortalFixture

TASK_SUMMARIES = ["task 0", "task 1", "task 2"]


def configure_portal(
    database_session: Session,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
    time_records_sent: list,
) -> None:
    portal_base_url = faker.url()
    kinds = database_session.scalars(sa.select(Kind)).all()
    kinds_config = {kind.alias: f"Category of {kind.alias}" for kind in kinds}
    projects = database_session.scalars(sa.select(Project)).all()
    projects_config = {project.alias: f"Portal project of {project.alias}" for project in projects}
    corp_struct_item = {"alias": "CORP", "id": 1, "name": "Corp struct item"}
    employee_id = 1
    reporting_config(
        {
            "app": {
                "minute-round-to": 15,
                "timezone": "UTC",
            },
            "qatestlab-portal": {
                "kinds": kinds_config,
                "login": "login",
                "password": "password",
                "projects": projects_config,
                "safe-send-report-days": 1,
                "url": portal_base_url,
            },
        }
    )
    portal_api_categories = [
        {
            "alias": f"CATEGORY{index}",
            "deleted": False,
            "id": index + 1,
            "name": category_name,
            "salaryCoefficient": 1,
        }
        for index, category_name in enumerate(kinds_config.values())
    ]
    portal_mock(
        base_url=portal_base_url,
        categories=portal_api_categories,
        category_bindings=[
            {
                "categoryId": portal_api_category["id"],
                "corpStructItemId": corp_struct_item["id"],
                "id": portal_api_category["id"],
                "positionId": 1,
                "roleId": 1,
            }
            for portal_api_category in portal_api_categories
        ],
        corp_struct_items=[corp_struct_item],
        init={
            "currentUser": {
                "user": {
                    "email": "employee@example.com",
                    "employeeId": employee_id,
                    "firstName": "First",
                    "lastName": "Last",
                    "login": "login",
                },
            },
        },
        employees_positions=[
            {
                "acting": False,
                "alias": "POSITION",
                "corpStructItemId": corp_struct_item["id"],
                "corpStructItemAlias": corp_struct_item["alias"],
                "employeeId": employee_id,
                "id": 1,
                "positionId": 1,
            }
        ],
        login={},
        logout={},
        providers={
            "clients": [],
            "projects": [
                {"active": True, "id": index + 1, "name": project_name}
                for index, project_name in enumerate(projects_config.values())
            ],
        },
        report=[],
        report_put=True,
        time_records_post=True,
        time_records_sent=time_records_sent,
    )


def create_report(report_date: datetime.date) -> None:
    kind = KindFactory.create(alias="dev", id=1, name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])
    report = ReportFactory.create(date=report_date, id=1, tasks=[])

    for index, summary in enumerate(TASK_SUMMARIES):
        TaskFactory.create(
            id=index + 1,
            kind=kind,
            kinds_id=kind.id,
            logged_seconds=60 * 60,
            project=project,
            projects_id=project.id,
            report=report,
            reports_id=report.id,
            summary=summary,
        )


def create_task(summary: str, logged_seconds: int, kind: Kind, project: Project, report: Report) -> Task:
    return TaskFactory.create(
        kind=kind,
        kinds_id=kind.id,
        logged_seconds=logged_seconds,
        project=project,
        projects_id=project.id,
        report=report,
        reports_id=report.id,
        summary=summary,
    )


def test_send_report(
    database_session: Session,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    portal_base_url = faker.url()

    create_report(datetime.datetime.now(datetime.UTC).date())

    kinds = database_session.scalars(sa.select(Kind)).all()
    kinds_config = {kind.alias: faker.sentence(nb_words=3, variable_nb_words=True) for kind in kinds}
    projects = database_session.scalars(sa.select(Project)).all()
    projects_config = {project.alias: faker.sentence(nb_words=3, variable_nb_words=True) for project in projects}
    projects_0_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
        "name": faker.sentence(nb_words=3, variable_nb_words=True),
    }
    current_user_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
        "name": faker.sentence(nb_words=3, variable_nb_words=True),
    }
    current_user_id = faker.random_int(min=1)
    reporting_config(
        {
            "app": {
                "minute-round-to": 15,
                "timezone": "UTC",
            },
            "qatestlab-portal": {
                "kinds": kinds_config,
                "login": faker.domain_word(),
                "password": faker.password(),
                "projects": projects_config,
                "project-to-corp-struct-item": {
                    projects[0].alias: projects_0_corp_struct_item["alias"],
                },
                "safe-send-report-days": 1,
                "url": portal_base_url,
            },
        }
    )
    portal_api_categories = [
        {
            "alias": faker.domain_word().upper(),
            "deleted": False,
            "id": faker.random_int(min=1),
            "name": kind_name,
            "salaryCoefficient": faker.random_int(min=1),
        }
        for kind_name in kinds_config.values()
    ]
    portal_api_category_bindings = [
        {
            "categoryId": portal_api_category["id"],
            "corpStructItemId": current_user_corp_struct_item["id"],
            "id": faker.random_int(min=1),
            "positionId": faker.random_int(min=1),
            "roleId": faker.random_int(min=1),
        }
        for portal_api_category in portal_api_categories
    ]
    portal_api_corp_struct_items = [
        {
            "alias": faker.domain_word().upper(),
            "id": faker.random_int(min=1),
            "name": faker.sentence(nb_words=3, variable_nb_words=True),
        },
        current_user_corp_struct_item,
        projects_0_corp_struct_item,
    ]
    portal_api_category_bindings.extend(
        [
            {
                "categoryId": portal_api_category["id"],
                "corpStructItemId": projects_0_corp_struct_item["id"],
                "id": faker.random_int(min=1),
                "positionId": faker.random_int(min=1),
                "roleId": faker.random_int(min=1),
            }
            for portal_api_category in portal_api_categories
        ]
    )
    portal_api_employees_positions = [
        {
            "acting": False,
            "alias": faker.domain_word().upper(),
            "corpStructItemId": corp_struct_item["id"],
            "corpStructItemAlias": corp_struct_item["alias"],
            "employeeId": current_user_id,
            "id": faker.random_int(min=1),
            "positionId": faker.random_int(min=1),
        }
        for corp_struct_item in portal_api_corp_struct_items
    ]
    portal_mock(
        base_url=portal_base_url,
        categories=portal_api_categories,
        category_bindings=portal_api_category_bindings,
        corp_struct_items=portal_api_corp_struct_items,
        init={
            "currentUser": {
                "user": {
                    "email": faker.email(),
                    "employeeId": current_user_id,
                    "firstName": faker.first_name(),
                    "lastName": faker.last_name(),
                    "login": faker.domain_word(),
                },
            },
        },
        employees_positions=portal_api_employees_positions,
        login={},
        logout={},
        providers={
            "clients": [],
            "projects": [
                {
                    "active": True,
                    "id": faker.random_int(min=1),
                    "name": project_name,
                }
                for project_name in projects_config.values()
            ],
        },
        report=[],
        report_put=True,
        time_records_post=True,
    )

    result = run_cli("send", "--portal")

    assert rendered_output.cells(result.out) == [["QATestLab Portal"]] + [
        ["\u2713", "01:00", summary, "My Project"] for summary in TASK_SUMMARIES
    ]


@pytest.mark.parametrize(
    "empty_response_data",
    [
        ("categories", "category_bindings"),
        ("corp_struct_items"),
        ("projects"),
    ],
)
def test_send_portal_empty_required_data(
    database_session: Session,
    empty_response_data: tuple,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    portal_base_url = faker.url()

    create_report(datetime.datetime.now(datetime.UTC).date())

    kinds = database_session.scalars(sa.select(Kind)).all()
    kinds_config = {kind.alias: faker.sentence(nb_words=3, variable_nb_words=True) for kind in kinds}
    projects = database_session.scalars(sa.select(Project)).all()
    projects_config = {project.alias: faker.sentence(nb_words=3, variable_nb_words=True) for project in projects}
    projects_0_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
        "name": faker.sentence(nb_words=3, variable_nb_words=True),
    }
    current_user_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
        "name": faker.sentence(nb_words=3, variable_nb_words=True),
    }
    current_user_id = faker.random_int(min=1)
    reporting_config(
        {
            "app": {
                "minute-round-to": 15,
            },
            "qatestlab-portal": {
                "kinds": kinds_config,
                "login": faker.domain_word(),
                "password": faker.password(),
                "projects": projects_config,
                "project-to-corp-struct-item": {
                    projects[0].alias: projects_0_corp_struct_item["alias"],
                },
                "safe-send-report-days": 1,
                "url": portal_base_url,
            },
        }
    )
    portal_api_categories = [
        {
            "id": faker.random_int(min=1),
            "name": kind_name,
            "salaryCoefficient": faker.random_int(min=1),
        }
        for kind_name in kinds_config.values()
    ]
    portal_api_corp_struct_items = [
        {
            "alias": faker.domain_word().upper(),
            "id": faker.random_int(min=1),
            "name": faker.sentence(nb_words=3, variable_nb_words=True),
        },
        current_user_corp_struct_item,
        projects_0_corp_struct_item,
    ]
    portal_api_category_bindings = [
        {
            "categoryId": portal_api_category["id"],
            "corpStructItemId": current_user_corp_struct_item["id"],
            "id": faker.random_int(min=1),
            "positionId": faker.random_int(min=1),
            "roleId": faker.random_int(min=1),
        }
        for portal_api_category in portal_api_categories
    ]
    portal_api_category_bindings.extend(
        [
            {
                "categoryId": portal_api_category["id"],
                "corpStructItemId": projects_0_corp_struct_item["id"],
                "id": faker.random_int(min=1),
                "positionId": faker.random_int(min=1),
                "roleId": faker.random_int(min=1),
            }
            for portal_api_category in portal_api_categories
        ]
    )
    portal_api_employees_positions = [
        {
            "acting": False,
            "alias": faker.domain_word().upper(),
            "corpStructItemId": corp_struct_item["id"],
            "corpStructItemAlias": corp_struct_item["alias"],
            "employeeId": current_user_id,
            "id": faker.random_int(min=1),
            "positionId": faker.random_int(min=1),
        }
        for corp_struct_item in portal_api_corp_struct_items
    ]
    portal_mock(
        base_url=portal_base_url,
        categories=portal_api_categories if "categories" in empty_response_data else [],
        category_bindings=portal_api_category_bindings if "category_bindings" in empty_response_data else [],
        corp_struct_items=portal_api_corp_struct_items if "corp_struct_items" in empty_response_data else [],
        init={
            "currentUser": {
                "user": {
                    "email": faker.email(),
                    "employeeId": current_user_id,
                    "firstName": faker.first_name(),
                    "lastName": faker.last_name(),
                    "login": faker.domain_word(),
                },
            },
        },
        employees_positions=portal_api_employees_positions,
        login={},
        logout={},
        providers=(
            {
                "clients": [],
                "projects": (
                    [
                        {
                            "active": True,
                            "id": faker.random_int(min=1),
                            "name": project_name,
                        }
                        for project_name in projects_config.values()
                    ]
                    if "projects" in empty_response_data
                    else []
                ),
            }
        ),
        report=[],
        report_put=True,
        time_records_post=True,
    )

    failure = run_cli("send", "--portal")

    assert failure.exit_code == 1
    assert failure.err == f"Failed tasks: {len(TASK_SUMMARIES)}\n"
    sent_cells = rendered_output.cells(failure.out)
    assert sent_cells[0] == ["QATestLab Portal"]

    for summary in TASK_SUMMARIES:
        assert ["\u2717", "01:00", summary, "My Project"] in sent_cells


def test_send_portal_keeps_a_task_without_a_key_as_its_own_record(
    database_session: Session,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    kind = KindFactory.create(alias="dev", id=1, name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])
    report = ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), tasks=[])
    create_task("TEST-1: text a", 60 * 60, kind, project, report)
    create_task("without a key", 60 * 60, kind, project, report)
    time_records_sent: list = []
    configure_portal(database_session, faker, portal_mock, reporting_config, time_records_sent)

    result = run_cli("send", "--portal")

    assert result.exit_code == 0
    assert [(time_record["description"], time_record["hours"]) for time_record in time_records_sent] == [
        ("TEST-1: text a", 100),
        ("without a key", 100),
    ]


def test_send_portal_keeps_the_same_key_apart_in_another_kind(
    database_session: Session,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    kind = KindFactory.create(alias="dev", id=1, name="Develop", tasks=[])
    other_kind = KindFactory.create(alias="rev", id=2, name="Review", tasks=[])
    project = ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])
    report = ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), tasks=[])
    create_task("TEST-1: text a", 60 * 60, kind, project, report)
    create_task("TEST-1: text b", 60 * 60, other_kind, project, report)
    time_records_sent: list = []
    configure_portal(database_session, faker, portal_mock, reporting_config, time_records_sent)

    result = run_cli("send", "--portal")

    assert result.exit_code == 0
    assert [(time_record["description"], time_record["hours"]) for time_record in time_records_sent] == [
        ("TEST-1: text a", 100),
        ("TEST-1: text b", 100),
    ]


def test_send_portal_merges_tasks_with_the_same_key_into_one_time_record(
    database_session: Session,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    kind = KindFactory.create(alias="dev", id=1, name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])
    report = ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), tasks=[])
    create_task("TEST-1: text a", 60 * 60, kind, project, report)
    create_task("TEST-1: text b", 60 * 60, kind, project, report)
    create_task("TEST-2: text c", 60 * 60, kind, project, report)
    time_records_sent: list = []
    configure_portal(database_session, faker, portal_mock, reporting_config, time_records_sent)

    result = run_cli("send", "--portal")

    assert result.exit_code == 0
    assert [
        (time_record["description"], time_record["hours"], time_record["orderNumber"])
        for time_record in time_records_sent
    ] == [
        ("TEST-1:\n- text a\n- text b", 200, 1),
        ("TEST-2: text c", 100, 2),
    ]
