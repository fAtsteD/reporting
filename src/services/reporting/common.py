"""
Common function of request to the reporting
"""

import requests
from requests.sessions import Session

from .api import ReportingApi

_reporting_api = None
_request_session = None


def get_api() -> ReportingApi:
    """
    Initialize api. Do requeired requests
    """
    global _reporting_api

    if _reporting_api is None:
        _reporting_api = ReportingApi(get_request_session())

        # Before any request for setting session
        if not _reporting_api.init():
            exit(_reporting_api.last_error)

        if not _reporting_api.login():
            exit(_reporting_api.last_error)

        if not _reporting_api.init():
            exit(_reporting_api.last_error)

        if not _reporting_api.load_categories():
            exit(_reporting_api.last_error)

        if not _reporting_api.load_projects():
            exit(_reporting_api.last_error)

        if not _reporting_api.load_positions():
            exit(_reporting_api.last_error)

    return _reporting_api


def get_request_session() -> Session:
    """
    Initialize request session
    """
    global _request_session

    if _request_session is None:
        _request_session = requests.Session()

    return _request_session
