import datetime
import json
from typing import Protocol

import faker
import pytest
from responses import RequestsMock, matchers
from sqlalchemy.orm import Session

from reporting import cli
from reporting.models.kind import Kind
from reporting.models.project import Project
from reporting.models.report import Report
from tests.conftest import ReportingConfigFixture
from tests.factories import ReportFactory


class PortalFixture(Protocol):

    def __call__(
        self,
        base_url: str,
        categories: dict | list | None = None,
        category_bindings: dict | list | None = None,
        corp_struct_items: dict | list | None = None,
        init: dict | None = None,
        employees_positions: dict | list | None = None,
        login: dict | None = None,
        logout: dict | None = None,
        providers: dict | None = None,
        report: dict | list | None = None,
        report_put: dict | None = None,
        time_record_post: dict | None = None,
    ) -> None: ...


@pytest.fixture
def portal_mock(responses: RequestsMock) -> PortalFixture:

    def requests_mock_portal(
        base_url: str,
        categories: dict | list | None = None,
        category_bindings: dict | list | None = None,
        corp_struct_items: dict | list | None = None,
        init: dict | None = None,
        employees_positions: dict | list | None = None,
        login: dict | None = None,
        logout: dict | None = None,
        providers: dict | None = None,
        report: dict | list | None = None,
        report_put: dict | None = None,
        time_record_post: dict | None = None,
    ) -> None:
        base_url = base_url.rstrip("/")

        if categories is not None:
            responses.add(
                responses.GET,
                f"{base_url}/common/categories",
                json=categories,
                status=200,
            )
        if category_bindings is not None:
            responses.add(
                responses.GET,
                f"{base_url}/category-binding",
                json=category_bindings,
                status=200,
            )
        if corp_struct_items is not None:
            responses.add(
                responses.GET,
                f"{base_url}/corp-struct-items",
                json=corp_struct_items,
                status=200,
            )
        if employees_positions is not None:
            responses.add(
                responses.GET,
                f"{base_url}/employees/positions",
                json=employees_positions,
                status=200,
            )
        if init is not None:
            responses.add(
                responses.GET,
                f"{base_url}/common/init",
                json=init,
                status=200,
            )
        if login is not None:
            responses.add(
                responses.POST,
                f"{base_url}/common/login",
                body=json.dumps(login) if login else "",
                status=200,
            )
        if logout is not None:
            responses.add(
                responses.POST,
                f"{base_url}/common/logout",
                body=json.dumps(logout) if logout else "",
                status=200,
            )
        if providers is not None:
            responses.add(
                responses.GET,
                f"{base_url}/providers",
                json=providers,
                status=200,
            )
        if report is not None:
            params: dict | None = None
            if isinstance(report, list) and len(report) > 0:
                params = {
                    "date": report[0]["date"],
                    "employeeId": report[0]["employeeId"],
                }
            responses.add(
                responses.GET,
                f"{base_url}/report",
                json=report,
                match=list(
                    filter(
                        lambda matcher: matcher,
                        [
                            matchers.query_param_matcher(params) if params else None,
                        ],
                    )
                ),
                status=200,
            )
        if report_put is not None:
            responses.add(
                responses.PUT,
                f"{base_url}/report",
                json=report_put,
                status=200,
            )
        if time_record_post is not None:
            responses.add(
                responses.POST,
                f"{base_url}/time-records",
                json=time_record_post,
                status=200,
            )

    return requests_mock_portal


@pytest.mark.parametrize(
    "report_date_today",
    [
        True,
        False,
    ],
)
def test_send_reporting_first_day_report(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    faker: faker.Faker,
    monkeypatch: pytest.MonkeyPatch,
    portal_mock: PortalFixture,
    report_date_today: bool,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_base_url = faker.url()
    report: Report = ReportFactory.create(
        date=(
            faker.date_between_dates(
                datetime.datetime(2000, 1, 1),
                datetime.datetime.now() - datetime.timedelta(days=10),
            )
            if not report_date_today
            else datetime.datetime.now()
        ),
    )
    kinds = database_session.query(Kind).all()
    kinds_config = {kind.alias: faker.sentence(nb_words=3, variable_nb_words=True) for kind in kinds}
    projects = database_session.query(Project).all()
    projects_config = {project.alias: faker.sentence(nb_words=3, variable_nb_words=True) for project in projects}
    projects_0_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
    }
    current_user_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
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
        },
        current_user_corp_struct_item,
        projects_0_corp_struct_item,
    ]
    portal_api_category_bindings = [
        {
            "categoryId": portal_api_category["id"],
            "corpStructItemId": current_user_corp_struct_item["id"],
        }
        for portal_api_category in portal_api_categories
    ]
    portal_api_category_bindings.extend(
        [
            {
                "categoryId": portal_api_category["id"],
                "corpStructItemId": projects_0_corp_struct_item["id"],
            }
            for portal_api_category in portal_api_categories
        ]
    )
    portal_mock(
        base_url=reporting_base_url,
        categories=portal_api_categories,
        category_bindings=portal_api_category_bindings,
        corp_struct_items=portal_api_corp_struct_items,
        init={
            "currentUser": {
                "user": {
                    "corpStructItemId": current_user_corp_struct_item["id"],
                    "employeeId": current_user_id,
                },
            },
        },
        employees_positions=[],
        login={},
        logout={},
        providers={
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
        report_put={
            "id": faker.random_int(min=1),
            "timeRecords": [],
        },
        time_record_post={},
    )
    if not report_date_today:
        monkeypatch.setattr("builtins.input", lambda _: "y")

    cli.main(["--reporting"])

    output = str(capsys.readouterr().out)
    assert output.startswith("Reporting\n")

    for task in report.tasks:
        assert output.find(f"[+] {task}\n") > -1


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
    report: Report = ReportFactory.create(date=datetime.datetime.now())
    kinds = database_session.query(Kind).all()
    kinds_config = {kind.alias: faker.sentence(nb_words=3, variable_nb_words=True) for kind in kinds}
    projects = database_session.query(Project).all()
    projects_config = {project.alias: faker.sentence(nb_words=3, variable_nb_words=True) for project in projects}
    projects_0_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
    }
    current_user_corp_struct_item = {
        "alias": faker.domain_word().upper(),
        "id": faker.random_int(min=1),
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
        },
        current_user_corp_struct_item,
        projects_0_corp_struct_item,
    ]
    portal_api_category_bindings = [
        {
            "categoryId": portal_api_category["id"],
            "corpStructItemId": current_user_corp_struct_item["id"],
        }
        for portal_api_category in portal_api_categories
    ]
    portal_api_category_bindings.extend(
        [
            {
                "categoryId": portal_api_category["id"],
                "corpStructItemId": projects_0_corp_struct_item["id"],
            }
            for portal_api_category in portal_api_categories
        ]
    )
    portal_mock(
        base_url=reporting_base_url,
        categories=portal_api_categories if "categories" in empty_response_data else [],
        category_bindings=portal_api_category_bindings if "category_bindings" in empty_response_data else [],
        corp_struct_items=portal_api_corp_struct_items if "corp_struct_items" in empty_response_data else [],
        init={
            "currentUser": {
                "user": {
                    "corpStructItemId": current_user_corp_struct_item["id"],
                    "employeeId": current_user_id,
                },
            },
        },
        employees_positions=[],
        login={},
        logout={},
        providers=(
            {
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
        report_put={
            "id": faker.random_int(min=1),
            "timeRecords": [],
        },
        time_record_post={},
    )

    cli.main(["--reporting"])

    output = str(capsys.readouterr().out)
    assert output.startswith("Reporting\n")

    for task in report.tasks:
        assert output.find(f"[-] {task}\n") > -1
