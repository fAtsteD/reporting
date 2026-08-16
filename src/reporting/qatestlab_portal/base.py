from typing import Any

from requests.exceptions import JSONDecodeError
from requests.models import Response
from requests.sessions import Session

from reporting.qatestlab_portal.exceptions import PortalRequestException


class BaseApi:
    def __init__(self, base_url: str, request_session: Session | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.base_url += "/reporting/api" if not self.base_url.endswith("reporting/api") else ""
        self._request_session = request_session or Session()

        self.ping()

    def ping(self) -> None:
        response = self._request_session.get(f"{self.base_url}/ping")

        if response.status_code >= 500:
            raise PortalRequestException("Portal reporting API is not available", response=response)

    def _get(self, endpoint: str, params: dict | None = None) -> Any:
        return self._request(method="get", endpoint=endpoint, params=params)

    def _post(self, endpoint: str, data: Any = None) -> Any:
        return self._request(method="post", endpoint=endpoint, data=data)

    def _put(self, endpoint: str, data: Any = None) -> Any:
        return self._request(method="put", endpoint=endpoint, data=data)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: Any = None,
    ) -> Any:
        endpoint = endpoint.strip("/")
        response: Response = self._request_session.request(
            json=data,
            method=method,
            params=params,
            url=f"{self.base_url}/{endpoint}",
        )

        if response.status_code >= 500:
            raise PortalRequestException(
                f"Portal reporting API {endpoint} has bad status code: {response.status_code}",
                response=response,
            )

        if response.status_code == 204:
            return None

        try:
            response_data = response.json()
        except JSONDecodeError:
            if response.status_code >= 400:
                raise PortalRequestException(f"Portal reporting API {endpoint} has bad body", response=response)

            return None

        if response.status_code >= 400:
            if isinstance(response_data, dict) and "errorMessage" in response_data:
                raise PortalRequestException(
                    f"Portal reporting API {endpoint} has error: {response_data['errorMessage']}",
                    response=response,
                )

            raise PortalRequestException(
                f"Portal reporting API {endpoint} has bad status code: {response.status_code}",
                response=response,
            )

        return response_data
