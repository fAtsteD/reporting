import datetime
import json
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from responses import RequestsMock

from reporting.qatestlab_portal.models import (
    Category,
    CategoryBinding,
    Client,
    CorpStructItem,
    EmployeePosition,
    Project,
    Report,
)
from tests.factories.portal_api import (
    PortalCategoryBindingFactory,
    PortalCategoryFactory,
    PortalClientFactory,
    PortalCorpStructItemFactory,
    PortalEmployeeFactory,
    PortalEmployeePositionFactory,
    PortalProjectFactory,
    PortalReportFactory,
)
from tests.fixtures.reporting_config import ReportingConfigFixture

_API_PATH = "/reporting/api"
_PORTAL_URL = "https://portal.example.com"

PORTAL_CONFIG: dict = {
    "app": {"timezone": "UTC"},
    "qatestlab-portal": {
        "login": "login",
        "password": "password",
        "url": _PORTAL_URL,
    },
}


class PortalApiFake:
    def __init__(self, responses: RequestsMock, base_url: str = _PORTAL_URL) -> None:
        self.base_url = base_url
        self.categories: list[Category] = []
        self.category_bindings: list[CategoryBinding] = []
        self.clients: list[Client] = []
        self.corp_struct_items: list[CorpStructItem] = []
        self.employee = PortalEmployeeFactory.build()
        self.employee_positions: list[EmployeePosition] = []
        self.projects: list[Project] = []
        self.reports: list[Report] = []
        self._report_save_fails = False
        self._responses = responses
        self._responses.assert_all_requests_are_fired = False
        self.corp_struct_item = self.add_corp_struct_item()
        self._register_routes()

    @property
    def saved_reports(self) -> list[dict]:
        return [json.loads(call.request.body or "{}") for call in self._calls("PUT", "report")]

    @property
    def sent_time_records(self) -> list[dict]:
        return [
            time_record
            for call in self._calls("POST", "time-records")
            for time_record in json.loads(call.request.body or "[]")
        ]

    def add_category(
        self,
        name: str,
        corp_struct_item: CorpStructItem | None = None,
        deleted: bool = False,
    ) -> Category:
        category = PortalCategoryFactory.build(deleted=deleted, name=name)
        self.categories.append(category)
        self.bind_category(category, corp_struct_item or self.corp_struct_item)

        return category

    def add_client(self, name: str) -> Client:
        client = PortalClientFactory.build(name=name)
        self.clients.append(client)

        return client

    def add_corp_struct_item(self, alias: str = "", employee_position: bool = True) -> CorpStructItem:
        corp_struct_item = PortalCorpStructItemFactory.build()

        if alias:
            corp_struct_item.alias = alias

        self.corp_struct_items.append(corp_struct_item)

        if employee_position:
            self.employee_positions.append(
                PortalEmployeePositionFactory.build(
                    corp_struct_item_alias=corp_struct_item.alias,
                    corp_struct_item_id=corp_struct_item.id,
                    employee_id=self.employee.id,
                )
            )

        return corp_struct_item

    def add_project(self, name: str, active: bool = True) -> Project:
        project = PortalProjectFactory.build(active=active, name=name)
        self.projects.append(project)

        return project

    def add_report(self, date: datetime.date, no_tasks: bool | None = False) -> Report:
        report = PortalReportFactory.build(date=date, employee_id=self.employee.id, no_tasks=no_tasks)
        self.reports.append(report)

        return report

    def assert_time_records_sent(self, expected: Sequence[Mapping[str, Any]]) -> None:
        sent = [
            {key: time_record.get(key) for key in expectation}
            for time_record, expectation in zip(self.sent_time_records, expected, strict=True)
        ]

        assert sent == [dict(expectation) for expectation in expected]

    def bind_category(self, category: Category, corp_struct_item: CorpStructItem) -> None:
        self.category_bindings.append(
            PortalCategoryBindingFactory.build(
                category_id=category.id,
                corp_struct_item_id=corp_struct_item.id,
            )
        )

    def fail_report_save(self) -> None:
        self._report_save_fails = True

    def forget_corp_struct_items(self) -> None:
        self.corp_struct_items.clear()

    def forget_employee_positions(self) -> None:
        self.employee_positions.clear()

    def _add_json_route(self, method: str, endpoint: str, payload: Any) -> None:
        self._responses.add_callback(
            method,
            self._url(endpoint),
            callback=lambda request: (200, {}, json.dumps(payload())),
            content_type="application/json",
        )

    def _calls(self, method: str, endpoint: str) -> list[Any]:
        url = self._url(endpoint)

        return [call for call in self._responses.calls if call.request.method == method and call.request.url == url]

    def _init_payload(self) -> dict:
        return {
            "currentUser": {
                "user": {
                    "email": self.employee.email,
                    "employeeId": self.employee.id,
                    "firstName": self.employee.first_name,
                    "lastName": self.employee.last_name,
                },
            },
        }

    def _provider_payload(self) -> dict:
        return {"clients": _dump(self.clients), "projects": _dump(self.projects)}

    def _register_routes(self) -> None:
        self._responses.add(self._responses.GET, self._url("ping"), status=204)
        self._responses.add(self._responses.POST, self._url("common/login"), body="")
        self._responses.add(self._responses.POST, self._url("common/logout"), body="")
        self._add_json_route(self._responses.GET, "common/categories", lambda: _dump(self.categories))
        self._add_json_route(self._responses.GET, "category-binding", lambda: _dump(self.category_bindings))
        self._add_json_route(self._responses.GET, "corp-struct-items", lambda: _dump(self.corp_struct_items))
        self._add_json_route(self._responses.GET, "employees/positions", lambda: _dump(self.employee_positions))
        self._add_json_route(self._responses.GET, "common/init", self._init_payload)
        self._add_json_route(self._responses.GET, "providers", self._provider_payload)
        self._add_json_route(self._responses.GET, "report", lambda: _dump(self.reports))
        self._responses.add_callback(
            self._responses.PUT,
            self._url("report"),
            callback=self._save_report,
            content_type="application/json",
        )
        self._responses.add_callback(
            self._responses.POST,
            self._url("time-records"),
            callback=self._save_time_records,
            content_type="application/json",
        )

    def _save_report(self, request: Any) -> tuple[int, dict, str]:
        report = json.loads(request.body)
        report["id"] = None if self._report_save_fails else report.get("id") or len(self.reports) + 1

        return 200, {}, json.dumps(report)

    def _save_time_records(self, request: Any) -> tuple[int, dict, str]:
        time_records = json.loads(request.body)

        for index, time_record in enumerate(time_records, start=1):
            time_record["id"] = time_record.get("id") or index

        return 200, {}, json.dumps(time_records)

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}{_API_PATH}/{endpoint}"


@pytest.fixture
def portal_api(responses: RequestsMock) -> PortalApiFake:
    return PortalApiFake(responses)


@pytest.fixture
def portal_config(reporting_config: ReportingConfigFixture) -> None:
    reporting_config(PORTAL_CONFIG)


def _dump(models: Sequence[Any]) -> list[dict]:
    return [model.model_dump(by_alias=True, mode="json") for model in models]
