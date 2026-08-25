from requests.models import Response

from reporting.exceptions import ReportingError


class PortalError(ReportingError):
    pass


class PortalRequestError(PortalError):
    def __init__(self, message: str, response: Response) -> None:
        super().__init__(message)
        self.response = response
