"""
Connection class to the reporting
"""

from datetime import datetime

import requests

from ...config_app import config
from ...transform import Task
from .categories import Categories
from .projects import Projects
from .report import Report
from .user import User


class ReportingApi:
    """
    Class save connection params to reporting
    """

    def __init__(self) -> None:
        """
        Connect to the server
        """
        if not config.reporting.can_use:
            exit("Used reporing module without required settings")

        self.request_session = requests.Session()

        self.last_error = None
        self.base_url = config.reporting.url
        self.is_auth = False

        self.user_data: User = None
        self.projects: Projects = None
        self.categories: Categories = None

    def login(self) -> None:
        """
        Auth in the reporting
        """
        data = {
            "login": config.reporting.login,
            "password": config.reporting.password
        }

        response = self.request_session.post(
            self.base_url + config.reporting.suburl_auth, json=data)

        if response.text == "":
            self.is_auth = True
            return True

        try:
            response_data = response.json()
        except Exception:
            self.is_auth = False
            self.last_error = "Can't parse JSON response for categories request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            self.is_auth = False
            return False

    def init(self) -> bool:
        """
        Init request for receiving requeired data
        """
        response = self.request_session.get(
            self.base_url + config.reporting.suburl_init)

        try:
            response_data = response.json()
        except Exception:
            self.user_data = None
            self.last_error = "Can't parse JSON response for init request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.user_data = User(response_data["currentUser"]["user"])

        return True

    def load_categories(self) -> bool:
        """
        Load categories from server
        """
        response = self.request_session.get(
            self.base_url + config.reporting.suburl_categories)

        try:
            response_data = response.json()
        except Exception:
            self.categories = None
            self.last_error = "Can't parse JSON response for categories request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.categories = Categories(response_data)

        return True

    def load_projects(self) -> bool:
        """
        Load projects from server
        """
        response = self.request_session.get(
            self.base_url + config.reporting.suburl_projects)

        try:
            response_data = response.json()
        except Exception:
            self.projects = None
            self.last_error = "Can't parse JSON response for project request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.projects = Projects(response_data["projects"])

        return True

    def get_reports(self, date: datetime) -> list:
        """
        Return report for the day
        Before the request need do init request
        """
        if self.user_data is None:
            self.last_error = "You need do init request before"
            return None

        data = {
            "date": date.strftime('%Y-%m-%d'),
            "employeeId": self.user_data.user["id"]
        }

        response = self.request_session.get(
            self.base_url + config.reporting.suburl_get_report, params=data)

        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for getting report request"
            return None

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return None

        result = []
        if len(response_data) > 0:
            for report in response_data:
                result.append(Report(report))

        return result

    def set_report(self, date: datetime, report_id: None, have_problems=False, has_tasks=True) -> Report:
        """
        Create report and return it
        """
        if self.user_data is None:
            self.last_error = "You need do init request before"
            return None

        data = {
            "date": date.strftime('%Y-%m-%d'),
            "employeeId": self.user_data.user["id"],
            "haveProblems": have_problems,
            "noTasks": not has_tasks,
            "problems": "",
        }

        if not report_id is None:
            data["id"] = report_id

        response = self.request_session.put(
            self.base_url + config.reporting.suburl_get_report, params=data)

        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for getting report request"
            return None

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return None

        return Report(response_data)

    def add_task(self, task: Task, report: Report) -> bool:
        """
        Add task to the report

        Report data has to be like response in the get report.

        In success server send tasks that you sent to it.
        """
        if self.user_data is None:
            self.last_error = "Need init request before"
            return False

        if self.categories is None:
            self.last_error = "Need load categories request before"
            return False

        if self.projects is None:
            self.last_error = "Need load projects request before"
            return False

        category = self.categories.get_by_name(task.kind)
        if category is None:
            self.last_error = "Category for " + task.kind + " does not find"
            return False

        project = self.projects.get_by_name(task.project)
        if project is None or not project["active"]:
            self.last_error = "Project for " + task.project + " does not find"
            return False

        data = [
            {
                "categoryId": category["id"],
                "clientId": self.user_data.user["id"],
                "departmentId": self.user_data.user["departmentId"],
                "description": task.name,
                "hours": int(task.get_transformed_time() * 100),
                "invoiceHours": 0,
                "orderNumber": report.next_task_order_num(),
                "overrideEmployeeId": None,
                "paidEvent": None,
                "pjmApproved": False,
                "pjmHours": None,
                "pomApproved": False,
                "projectId": project["id"],
                "reportId": report.report["id"],
                "salaryCoefficient": category["salaryCoefficient"],
                "salaryCoefficientType": 0
            }
        ]

        response = self.request_session.post(
            self.base_url + config.reporting.suburl_add_task, json=data)

        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for getting report request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        return True
