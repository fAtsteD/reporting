import pytest
from responses import RequestsMock

from reporting.qatestlab_portal.base import BaseApi
from reporting.qatestlab_portal.exceptions import PortalRequestError

_BASE_URL = "https://portal.example.com"
_API_URL = f"{_BASE_URL}/reporting/api"


def test_appends_the_api_path_to_the_base_url(responses: RequestsMock) -> None:
    assert _build_api(responses).base_url == _API_URL


def test_keeps_the_api_path_that_is_already_in_the_base_url(responses: RequestsMock) -> None:
    responses.add(responses.GET, f"{_API_URL}/ping", status=204)

    assert BaseApi(_API_URL).base_url == _API_URL


def test_reads_no_body_from_a_no_content_response(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", status=204)

    assert api._get("thing") is None


def test_reads_no_body_from_a_successful_response_that_is_not_json(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", body="not json", status=200)

    assert api._get("thing") is None


def test_reads_the_json_body_of_a_successful_response(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", json={"name": "value"}, status=200)

    assert api._get("thing") == {"name": "value"}


def test_rejects_a_client_error_whose_body_is_not_json(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", body="not json", status=400)

    with pytest.raises(PortalRequestError, match="has bad body"):
        api._get("thing")


def test_rejects_a_client_error_without_an_error_message(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", json={"other": "value"}, status=404)

    with pytest.raises(PortalRequestError, match="has bad status code: 404"):
        api._get("thing")


def test_rejects_a_portal_that_is_not_available(responses: RequestsMock) -> None:
    responses.add(responses.GET, f"{_API_URL}/ping", status=503)

    with pytest.raises(PortalRequestError, match="Portal reporting API is not available"):
        BaseApi(_BASE_URL)


def test_rejects_a_server_error(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", status=500)

    with pytest.raises(PortalRequestError, match="has bad status code: 500"):
        api._get("thing")


def test_reports_the_error_message_of_a_client_error(responses: RequestsMock) -> None:
    api = _build_api(responses)
    responses.add(responses.GET, f"{_API_URL}/thing", json={"errorMessage": "Not allowed"}, status=403)

    with pytest.raises(PortalRequestError, match="has error: Not allowed"):
        api._get("thing")


def _build_api(responses: RequestsMock) -> BaseApi:
    responses.add(responses.GET, f"{_API_URL}/ping", status=204)

    return BaseApi(_BASE_URL)
