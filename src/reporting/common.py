"""
Common function of request to the reporting
"""

import requests
from requests.sessions import Session

from .api import ReportingApi
from .site import ReportingSite

_reporting_api = None
_reporting_site = None
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


def get_site() -> ReportingSite:
    """
    Initialize site. Do requeired requests
    """
    global _reporting_site

    if _reporting_site is None:
        _reporting_site = ReportingSite(get_request_session())

        if _reporting_site.login() == "":
            exit(_reporting_site.last_error)

    return _reporting_site


def get_request_session() -> Session:
    """
    Initialize request session
    """
    global _request_session

    if _request_session is None:
        _request_session = requests.Session()

    return _request_session
