import pytest
from responses import RequestsMock

from reporting.qatestlab_portal.client import QATestLabPortal
from reporting.qatestlab_portal.exceptions import PortalError
from reporting.qatestlab_portal.models import Employee

_BASE_URL = "https://portal.example.com"
_API_URL = f"{_BASE_URL}/reporting/api"


def test_reads_the_employee_from_the_init_response() -> None:
    employee = Employee.from_init(
        {
            "currentUser": {
                "user": {
                    "email": "someone@example.com",
                    "employeeId": 7,
                    "firstName": "First",
                    "lastName": "Last",
                },
            },
        }
    )

    assert (employee.email, employee.id, employee.first_name, employee.last_name) == (
        "someone@example.com",
        7,
        "First",
        "Last",
    )


def test_rejects_a_providers_response_without_a_body(responses: RequestsMock) -> None:
    portal = _build_portal(responses)
    responses.add(responses.GET, f"{_API_URL}/providers", status=204)

    with pytest.raises(PortalError, match="providers has unexpected body"):
        portal.providers()


@pytest.mark.parametrize(
    "body, status",
    [
        pytest.param({"clients": []}, 200, id="the projects are missing"),
        pytest.param({"projects": []}, 200, id="the clients are missing"),
        pytest.param([], 200, id="the body is not an object"),
    ],
)
def test_rejects_a_providers_response_without_clients_and_projects(
    body: object,
    responses: RequestsMock,
    status: int,
) -> None:
    portal = _build_portal(responses)
    responses.add(responses.GET, f"{_API_URL}/providers", json=body, status=status)

    with pytest.raises(PortalError, match="providers has unexpected body"):
        portal.providers()


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="no current user"),
        pytest.param({"currentUser": {}}, id="no user in the current user"),
    ],
)
def test_rejects_an_init_response_without_the_current_user(data: dict) -> None:
    with pytest.raises(PortalError, match="does not have the current user"):
        Employee.from_init(data)


def test_rejects_an_init_user_that_misses_a_field() -> None:
    data = {
        "currentUser": {
            "user": {"email": "someone@example.com", "employeeId": 7, "lastName": "Last"},
        },
    }

    with pytest.raises(PortalError, match="does not have the field 'firstName'"):
        Employee.from_init(data)


def _build_portal(responses: RequestsMock) -> QATestLabPortal:
    responses.add(responses.GET, f"{_API_URL}/ping", status=204)
    responses.add(responses.POST, f"{_API_URL}/common/login", body="")
    portal = QATestLabPortal(_BASE_URL)
    portal.login("login", "password")

    return portal
