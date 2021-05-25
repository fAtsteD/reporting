"""
Common function of request to the reporting
"""

from .api import ReportingApi

_reporting_api = None


def get_api() -> ReportingApi:
    """
    Initialize api. Do requeired requests
    """
    global _reporting_api

    if _reporting_api is None:
        _reporting_api = ReportingApi()
        _reporting_api.login()

        if not _reporting_api.is_auth:
            exit("Cannot auth in reporting")

        if not _reporting_api.init():
            exit(_reporting_api.last_error)

        if not _reporting_api.load_categories():
            exit(_reporting_api.last_error)

        if not _reporting_api.load_projects():
            exit(_reporting_api.last_error)

    return _reporting_api
