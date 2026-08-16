from requests.models import Response


class PortalException(Exception):
    pass


class PortalNotAuthorizedException(PortalException):
    pass


class PortalRequestException(PortalException):
    def __init__(self, message: str, response: Response) -> None:
        super().__init__(message)
        self.response = response
