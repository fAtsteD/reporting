import datetime
from enum import Enum

import faker
import pytest
from sqlalchemy.orm import Session

from reporting import cli
from reporting.models import Kind, Project
from tests.conftest import ReportingConfigFixture
from tests.factories import ReportFactory
from tests.fixtures.portal import PortalFixture


class ReportDates(Enum):
    Future = "future"
    Past = "past"
    Today = "today"


@pytest.mark.parametrize(
    "report_date_type",
    [
        ReportDates.Today,
        ReportDates.Past,
        ReportDates.Future,
    ],
)
def test_send_report(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    faker: faker.Faker,
    monkeypatch: pytest.MonkeyPatch,
    portal_mock: PortalFixture,
    report_date_type: ReportDates,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_base_url = faker.url()
    report_date: datetime.date | None = None
    call_input_count = 0

    def check_input(_) -> str:
        nonlocal call_input_count
        call_input_count += 1
        return "y"

    monkeypatch.setattr("builtins.input", check_input)

    match report_date_type:
        case ReportDates.Future:
            report_date = faker.date_between_dates(
                datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=2),
                datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=10),
            )
        case ReportDates.Past:
            report_date = faker.date_between_dates(
                datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC),
                datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=10),
            )
        case ReportDates.Today:
            report_date = datetime.datetime.now(datetime.UTC).date()

    report = ReportFactory.create(
        date=report_date,
    )
    kinds = database_session.query(Kind).all()
    kinds_config = {kind.alias: faker.sentence(nb_words=3, variable_nb_words=True) for kind in kinds}
    projects = database_session.query(Project).all()
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
            "minute-round-to": 15,
            "reporting": {
                "kinds": kinds_config,
                "login": faker.domain_word(),
                "password": faker.password(),
                "projects": projects_config,
                "project-to-corp-struct-item": {
                    projects[0].alias: projects_0_corp_struct_item["alias"],
                },
                "safe-send-report-days": 1,
                "url": reporting_base_url,
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
        base_url=reporting_base_url,
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

    cli.main(["--reporting"])

    output = str(capsys.readouterr().out)
    assert output.startswith("Reporting\n")

    for task in report.tasks:
        assert output.find(f"[+] {task}\n") > -1

    match report_date_type:
        case ReportDates.Future:
            assert call_input_count == 1, "Input should be called once for future report date"
        case ReportDates.Past:
            assert call_input_count == 1, "Input should be called once for past report date"
        case ReportDates.Today:
            assert call_input_count == 0, "Input should not be called for today report date"


@pytest.mark.parametrize(
    "empty_response_data",
    [
        ("categories", "category_bindings"),
        ("corp_struct_items"),
        ("projects"),
    ],
)
def test_send_reporting_empty_required_data(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    empty_response_data: tuple,
    faker: faker.Faker,
    portal_mock: PortalFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_base_url = faker.url()
    report = ReportFactory.create(date=datetime.datetime.now(datetime.UTC))
    kinds = database_session.query(Kind).all()
    kinds_config = {kind.alias: faker.sentence(nb_words=3, variable_nb_words=True) for kind in kinds}
    projects = database_session.query(Project).all()
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
            "minute-round-to": 15,
            "reporting": {
                "kinds": kinds_config,
                "login": faker.domain_word(),
                "password": faker.password(),
                "projects": projects_config,
                "project-to-corp-struct-item": {
                    projects[0].alias: projects_0_corp_struct_item["alias"],
                },
                "safe-send-report-days": 1,
                "url": reporting_base_url,
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
        base_url=reporting_base_url,
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

    cli.main(["--reporting"])

    output = str(capsys.readouterr().out)
    assert output.startswith("Reporting\n")

    for task in report.tasks:
        assert output.find(f"[-] {task}\n") > -1
