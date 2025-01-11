class PortalException(Exception):
    pass


class PortalRequestException(PortalException):
    def __init__(self, message, response):
        super().__init__(message)
        self.response = response
