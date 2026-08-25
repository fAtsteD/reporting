import datetime

import faker
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Kind, Project
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import RunCli
from tests.fixtures.portal import PortalFixture

TASK_SUMMARIES = ["task 0", "task 1", "task 2"]


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

    assert result.out == "QATestLab Portal\n" + "".join(
        f"[+] 01:00 - {summary} - My Project\n" for summary in TASK_SUMMARIES
    )


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
    assert failure.out.startswith("QATestLab Portal\n")

    for summary in TASK_SUMMARIES:
        assert f"[-] 01:00 - {summary} - My Project\n" in failure.out
