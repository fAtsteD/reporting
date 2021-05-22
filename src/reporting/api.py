"""
Connection class to the reporting
"""

from datetime import datetime

import requests

from ..config_app import config
from ..transform import Task


class ReportingApi:
    """
    Class save connection params to reporting
    """

    def __init__(self, login: str, password: str):
        """
        Connect to the server
        """
        self.request_session = requests.Session()
        self.login = login
        self.password = password

        self.last_error = ""
        self.base_url = config.reporting.url
        self.is_auth = False

        self.user_data = {}
        self.projects = []
        self.categories = []

    def _login(self):
        """
        Auth in the reporting
        """
        data = {
            "login": self.login,
            "password": self.password
        }
        response = self.request_session.post(
            self.base_url + config.reporting.auth_suburl, json=data)

        if response.text == "1":
            self.is_auth = True

    def init(self) -> bool:
        """
        Init request for receiving requeired data
        """
        response = self.request_session.get(
            self.base_url + config.reporting.suburl_init)

        try:
            response_data = response.json()
        except Exception:
            self.user_data = {}
            self.last_error = "Can't parse JSON response for init request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.user_data = response_data["currentUser"]["user"]

        return True

    def load_categories(self) -> bool:
        """
        Load categories from server
        """
        response = self.request_session.get(
            self.base_url + config.reporting.categories_suburl)

        try:
            response_data = self.categories = response.json()
        except Exception:
            self.categories = []
            self.last_error = "Can't parse JSON response for categories request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.categories = response_data

        return True

    def load_projects(self) -> bool:
        """
        Load projects from server
        """
        response = self.request_session.get(
            self.base_url + config.reporting.projects_suburl)

        try:
            response_data = self.projects = response.json()
        except Exception:
            self.projects = []
            self.last_error = "Can't parse JSON response for project request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.projects = response_data

        return True

    def get_report(self, date: datetime) -> dict:
        """
        Return report for the day
        Before the request need do init request
        """
        if len(self.user_data) == 0:
            self.last_error = "You need do init request before"
            return False

        data = {
            "date": str(date.year) + "-" + str(date.month) + "-" + str(date.day),
            "employeeId": self.user_data["id"]
        }

        response = self.request_session.get(
            self.base_url + config.reporting.suburl_get_report, params=data)
        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for getting report request"
            return {}

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return {}

        return response_data[0]

    def add_task(self, task: Task, report: dict) -> bool:
        """
        Add task to the report

        Report data has to be like response in the get report
        """
        if len(self.last_report) == 0:
            return False

        # TODO: Set data to the request and send it
        data = {
            "categoryId": 0,
            "clientId": None,
            "departmentId": 0,
            "description": "",
            "hours": 0,
            "invoiceHours": 0,
            "orderNumber": 0,
            "overrideEmployeeId": None,
            "paidEvent": None,
            "pjmApproved": False,
            "pjmHours": None,
            "pomApproved": False,
            "projectId": 0,
            "reportId": 0,
            "salaryCoefficient": 0,
            "salaryCoefficientType": 0
        }
