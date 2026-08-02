import json
from typing import Protocol

import faker
import pytest
from responses import RequestsMock, matchers


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
        report_put: bool = False,
        time_records_post: bool = False,
    ) -> None: ...


@pytest.fixture
def portal_mock(
    responses: RequestsMock,
    faker: faker.Faker,
) -> PortalFixture:

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
        report_put: bool = False,
        time_records_post: bool = False,
    ) -> None:
        responses.assert_all_requests_are_fired = False
        base_url = base_url.rstrip("/") + "/reporting/api"

        responses.add(
            responses.GET,
            f"{base_url}/ping",
            status=204,
        )

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
        if report_put:

            def report_put_callback(request):
                request_body = json.loads(request.body)
                request_body["id"] = (
                    request_body["id"]
                    if "id" in request_body and request_body["id"] and request_body["id"] > 0
                    else faker.random_int(min=1)
                )
                return 200, {}, json.dumps(request_body)

            responses.add_callback(
                responses.PUT,
                f"{base_url}/report",
                callback=report_put_callback,
                content_type="application/json",
            )
        if time_records_post:

            def time_records_post_callback(request):
                request_body = json.loads(request.body)
                for time_record in request_body:
                    time_record["id"] = (
                        time_record["id"]
                        if "id" in time_record and time_record["id"] and time_record["id"] > 0
                        else faker.random_int(min=1)
                    )
                return 200, {}, json.dumps(request_body)

            responses.add_callback(
                responses.POST,
                f"{base_url}/time-records",
                callback=time_records_post_callback,
                content_type="application/json",
            )

    return requests_mock_portal
