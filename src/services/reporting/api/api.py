"""
Connection class to the reporting
"""

from datetime import datetime

from requests.sessions import Session

from config_app import config
from models.task import Task

from .categories import Categories
from .positions import Positions
from .projects import Projects
from .report import Report
from .user import User


def transform_time(seconds: int) -> int:
    """
    Transform seconds to the hours and minutes with
    mapping from 0-60 to 0-100
    """
    return round(seconds / 60 / 60 * 100)


class ReportingApi:
    """
    Class save connection params to reporting
    """

    def __init__(self, request_session: Session) -> None:
        """
        Connect to the server
        """
        if not config.reporting.is_use:
            exit("Used reporting module without required settings")

        self._request_session = request_session

        self.last_error = None
        self.base_url = config.reporting.url
        self.is_auth = False

        self.user_data: User | None = None
        self.projects: Projects | None = None
        self.positions: Positions | None = None
        self.categories: Categories | None = None

    def login(self) -> bool:
        """
        Auth in the reporting
        """
        self.last_error = None
        data = {
            "login": config.reporting.login,
            "password": config.reporting.password
        }

        response = self._request_session.post(
            self.base_url + config.reporting.suburl_auth, json=data)

        if response.text == "":
            self.is_auth = True
            return True

        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for login request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

    def logout(self) -> bool:
        """
        Log out from the reporting
        """
        response = self._request_session.post(
            self.base_url + config.reporting.suburl_logout
        )

        if response.text == "":
            self.is_auth = False
            return True

        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for logout request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

    def init(self) -> bool:
        """
        Init request for receiving required data
        """
        response = self._request_session.get(
            self.base_url + config.reporting.suburl_init
        )

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
        response_categories = self._request_session.get(
            self.base_url + config.reporting.suburl_categories
        )
        response_categories_binding = self._request_session.get(
            self.base_url + config.reporting.suburl_categories_binding
        )

        try:
            response_data_categories = response_categories.json()
            response_data_categories_binding = response_categories_binding.json()
        except Exception:
            self.categories = None
            self.last_error = "Can't parse JSON response for categories request"
            return False

        if "error" in response_data_categories:
            self.last_error = response_data_categories["errorMessage"]
            return False

        if "error" in response_data_categories_binding:
            self.last_error = response_data_categories_binding["errorMessage"]
            return False

        self.categories = Categories(
            response_data_categories, response_data_categories_binding)

        return True

    def load_projects(self) -> bool:
        """
        Load projects from server
        """
        response = self._request_session.get(
            self.base_url + config.reporting.suburl_projects
        )

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

    def load_positions(self) -> bool:
        """
        Load privileges by user from server

        Also update user data if it is not empty.
        """
        response = self._request_session.get(
            self.base_url + config.reporting.suburl_positions
        )

        try:
            response_data = response.json()
        except Exception:
            self.positions = None
            self.last_error = "Can't parse JSON response for positions request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.positions = Positions(response_data)

        if self.user_data is not None:
            user_position = self.positions.get_by_user_id(
                self.user_data.get_id()
            )
            del user_position["id"]
            self.user_data.update_data(user_position)

        return True

    def get_reports(self, date: datetime) -> list[Report] | None:
        """
        Return report for the day
        Before the request need do init request
        """
        self.last_error = None

        if self.user_data is None:
            self.last_error = "You need do init request before"
            return None

        data = {
            "date": date.strftime('%Y-%m-%d'),
            "employeeId": self.user_data.get_id()
        }

        response = self._request_session.get(
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

    def set_report(self, date: datetime, report_id: None, have_problems=False, has_tasks=True) -> Report | None:
        """
        Create report and return it
        """
        self.last_error = None

        if self.user_data is None:
            self.last_error = "You need do init request before"
            return None

        data = {
            "date": date.strftime('%Y-%m-%d'),
            "employeeId": self.user_data.get_id(),
            "haveProblems": have_problems,
            "noTasks": not has_tasks,
            "problems": "",
        }

        if report_id is not None:
            data["id"] = report_id

        response = self._request_session.put(
            self.base_url + config.reporting.suburl_get_report, json=data)

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
        self.last_error = None

        if self.user_data is None:
            self.last_error = "Need init request before"
            return False

        if self.categories is None:
            self.last_error = "Need load categories request before"
            return False

        if self.projects is None:
            self.last_error = "Need load projects request before"
            return False

        category = self._get_category_by_task(task)

        if not category:
            self.last_error = "Category for " + task.kind + " does not find"
            return False

        project = self._get_project_by_task(task)

        if project is None or not project["active"]:
            self.last_error = "Project for " + task.project + " does not find"
            return False

        data = [
            {
                "categoryId": category["id"],
                "clientId": self.user_data.get_id(),
                "corpStructItemId": self.user_data.get_corp_struct_id(),
                "description": task.summary,
                "hours": transform_time(task.logged_rounded()),
                "invoiceHours": 0,
                "orderNumber": report.next_task_order_num(),
                "overrideEmployeeId": None,
                "paidEvent": None,
                "pjmApproved": False,
                "pjmHours": None,
                "pomApproved": False,
                "projectId": project["id"],
                "reportId": report.get_id(),
                "salaryCoefficient": category["salaryCoefficient"],
                "salaryCoefficientType": 0
            }
        ]

        response = self._request_session.post(
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

    def _get_category_by_task(self, task: Task) -> dict:
        """
        Return category dict from reporting for task

        It searches by name, but before searching it transform saved
        kind to the related report kinds
        """
        kind = task.kind
        category_name = kind.name

        if kind.alias in config.reporting.kinds.keys():
            category_name = config.reporting.kinds[kind.alias]

        return self.categories.get_by_name(
            category_name,
            self.user_data.get_corp_struct_id()
        )

    def _get_project_by_task(self, task: Task) -> dict:
        """
        Return project dict from reporting for task

        It searches by name, but before searching it transform saved
        project to the related report projects
        """
        project = task.project
        project_name = project.name

        if project.alias in config.reporting.projects.keys():
            project_name = config.reporting.projects[project.alias]

        return self.projects.get_by_name(
            project_name
        )
