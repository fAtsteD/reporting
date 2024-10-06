import datetime

from requests.sessions import Session

from reporting import config_app
from reporting.models.kind import Kind
from reporting.models.project import Project
from reporting.models.task import Task
from reporting.services.reporting.models.categories import Categories
from reporting.services.reporting.models.corp_struct_items import CorpStructItems
from reporting.services.reporting.models.positions import Positions
from reporting.services.reporting.models.projects import Projects
from reporting.services.reporting.models.report import Report
from reporting.services.reporting.models.user import User


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

    def __init__(self, request_session: Session = Session()) -> None:
        """
        Connect to the server
        """
        config = config_app.config

        if not config.reporting.is_use:
            exit("Used reporting module without required settings")

        self._request_session = request_session

        self.last_error: str | None = None
        self.base_url = config.reporting.url[:-1] if config.reporting.url.endswith("/") else config.reporting.url
        self.is_auth = False

        self.categories: Categories | None = None
        self.corp_struct_items: CorpStructItems | None = None
        self.positions: Positions | None = None
        self.projects: Projects | None = None
        self.user_data: User | None = None

    def login(self) -> bool:
        config = config_app.config
        self.last_error = None
        data = {"login": config.reporting.login, "password": config.reporting.password}

        response = self._request_session.post(f"{self.base_url}/common/login", json=data)

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

        return True

    def logout(self) -> bool:
        response = self._request_session.post(f"{self.base_url}/common/logout")

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

        return True

    def init(self) -> bool:
        response = self._request_session.get(f"{self.base_url}/common/init")

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
        response_categories = self._request_session.get(f"{self.base_url}/common/categories")
        response_categories_binding = self._request_session.get(f"{self.base_url}/category-binding")

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

        self.categories = Categories(response_data_categories, response_data_categories_binding)

        return True

    def load_projects(self) -> bool:
        """
        Load projects from server
        """
        response = self._request_session.get(f"{self.base_url}/providers")

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

    def load_corp_struct_items(self) -> bool:
        """
        Load corp struct items by user from server
        """
        response = self._request_session.get(f"{self.base_url}/corp-struct-items")

        try:
            response_data = response.json()
        except Exception:
            self.corp_struct_items = None
            self.last_error = "Can't parse JSON response for corp struct items request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        self.corp_struct_items = CorpStructItems(response_data)

        return True

    def load_positions(self) -> bool:
        """
        Load positions from server
        """
        response = self._request_session.get(f"{self.base_url}/employees/positions")

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
            user_position = self.positions.get_by_user_id(self.user_data.get_id())

            if user_position is not None:
                del user_position["id"]
                self.user_data.update_data(user_position)

        return True

    def get_reports(self, date: datetime.date) -> list[Report] | None:
        """
        Return report for the day
        Before the request need do init request
        """
        self.last_error = None

        if self.user_data is None:
            self.last_error = "You need do init request before"
            return None

        data: dict = {
            "date": date.strftime("%Y-%m-%d"),
            "employeeId": self.user_data.get_id(),
        }

        response = self._request_session.get(f"{self.base_url}/report", params=data)

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

    def set_report(
        self, date: datetime.date, report_id: int | None = None, have_problems=False, has_tasks=True
    ) -> Report | None:
        """
        Create report and return it
        """
        self.last_error = None

        if self.user_data is None:
            self.last_error = "You need do init request before"
            return None

        data = {
            "date": date.strftime("%Y-%m-%d"),
            "employeeId": self.user_data.get_id(),
            "haveProblems": have_problems,
            "noTasks": not has_tasks,
            "problems": "",
        }

        if report_id is not None:
            data["id"] = report_id

        response = self._request_session.put(f"{self.base_url}/report", json=data)

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

        if self.corp_struct_items is None:
            self.last_error = "Need load corp struct items request before"
            return False

        if self.categories is None:
            self.last_error = "Need load categories request before"
            return False

        if self.projects is None:
            self.last_error = "Need load projects request before"
            return False

        corp_struct_item = self._get_corp_struct_item_by_task(task)

        if not corp_struct_item:
            self.last_error = "Corp struct item for " + str(task.project) + " does not find"
            return False

        category = self._get_category_by_task(task, corp_struct_item["id"])

        if not category:
            self.last_error = "Category for " + str(task.kind) + " does not find"
            return False

        project = self._get_project_by_task(task)

        if project is None or not project["active"]:
            self.last_error = "Project for " + str(task.project) + " does not find"
            return False

        data = [
            {
                "categoryId": category["id"],
                "clientId": self.user_data.get_id(),
                "corpStructItemId": corp_struct_item["id"],
                "description": task.summary,
                "hours": transform_time(task.logged_rounded),
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
                "salaryCoefficientType": 0,
            }
        ]

        response = self._request_session.post(f"{self.base_url}/time-records", json=data)

        try:
            response_data = response.json()
        except Exception:
            self.last_error = "Can't parse JSON response for getting report request"
            return False

        if "error" in response_data:
            self.last_error = response_data["errorMessage"]
            return False

        return True

    def _get_category_by_task(self, task: Task, corp_struct_item_id: int) -> dict | None:
        """
        Return category dict from reporting for task

        It searches by name, but before searching it transform saved
        kind to the related report kinds
        """
        if not self.categories:
            return None

        config = config_app.config
        kind: Kind = task.kind
        category_name = kind.name

        if kind.alias in config.reporting.kinds.keys():
            category_name = config.reporting.kinds[kind.alias]

        return self.categories.get_by_name(category_name, corp_struct_item_id)

    def _get_corp_struct_item_by_task(self, task: Task) -> dict | None:
        """
        Return corp struct item dict from reporting for task

        It uses project for searching corp struct item
        by relational from config of app
        """
        if not self.corp_struct_items:
            return None

        config = config_app.config
        project: Project = task.project
        user_corp_struct_item_id = self.user_data.get_corp_struct_item_id() if self.user_data else None

        if project.alias in config.reporting.project_to_corp_struct_item.keys():
            corp_struct_item_alias = config.reporting.project_to_corp_struct_item[project.alias]
            return self.corp_struct_items.get_by_alias(corp_struct_item_alias)

        return self.corp_struct_items.get_by_id(user_corp_struct_item_id) if user_corp_struct_item_id else None

    def _get_project_by_task(self, task: Task) -> dict | None:
        """
        Return project dict from reporting for task

        It searches by name, but before searching it transform saved
        project to the related report projects
        """
        if not self.projects:
            return None

        config = config_app.config
        project: Project = task.project
        project_name = project.name

        if project.alias in config.reporting.projects.keys():
            project_name = config.reporting.projects[project.alias]

        return self.projects.get_by_name(project_name)
