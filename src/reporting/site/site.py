"""
Connection class to the reporting site
"""

from requests.sessions import Session

from ...config_app import config


class ReportingSite:
    """
    Class save connection params to reporting
    """

    def __init__(self, request_session: Session) -> None:
        """
        Connect to the server
        """
        if not config.reporting.can_use:
            exit("Used reporing module without required settings")

        self.request_session = request_session

        self.last_error = None
        self.base_url = config.reporting.site_url

    def login(self) -> str:
        """
        Request for login page even if you logged in.
        Set session cookie in that request for authenticated user
        """
        response = self.request_session.get(
            self.base_url + config.reporting.suburl_page_login)

        if response.text != "" and response.status_code < 400:
            return response.text
        else:
            self.last_error = "Login page empty or status code wrong. Status code: " + \
                response.status_code
            return ""
