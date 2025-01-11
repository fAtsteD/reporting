import datetime
from typing import TypedDict

from reporting.qatestlab_portal.reporting.api import ReportingApi
from reporting.qatestlab_portal.reporting.models import Employee, Report, TimeRecord
from reporting.qatestlab_portal.reporting.repositories import (
    CategoryRepository,
    CorpStructItemRepository,
    EmployeePositionRepository,
    ProvidersRepository,
)


class ReportingClientRepositories(TypedDict, total=False):
    category: CategoryRepository
    corp_struct_item: CorpStructItemRepository
    employee_position: EmployeePositionRepository
    providers: ProvidersRepository


class ReportingClient:

    def __init__(self, base_url: str) -> None:
        self._api = ReportingApi(base_url=base_url)
        self._employee: Employee | None = None
        self._is_login = False
        self._repositories: ReportingClientRepositories = {}

    @property
    def employee(self) -> Employee | None:
        if self._is_login and not self._employee:
            self._employee = self._api.init()

        return self._employee

    def login(self, login: str, password: str) -> None:
        self._is_login = self._api.login(login=login, password=password)

    def logout(self) -> None:
        self._is_login = False
        self._api.logout()
        self._employee = None
        self._repositories = {}

    def report_save(self, report: Report) -> Report:
        return self._api.report_save(report=report)

    def reports(self, date: datetime.date) -> list[Report]:
        if not self.employee:
            return []

        return list(self._api.reports(date=date, employee_id=self.employee.id))

    def repositoryCategory(self, reload: bool = False) -> CategoryRepository:
        if ("category" not in self._repositories or reload) and self._is_login:
            self._repositories["category"] = CategoryRepository(
                categories=list(self._api.categories()),
                categories_binding=list(self._api.categories_bindings()),
            )

        return self._repositories["category"] if "category" in self._repositories else CategoryRepository([], [])

    def repositoryCorpStructItem(self, reload: bool = False) -> CorpStructItemRepository:
        if ("corp_struct_item" not in self._repositories or reload) and self._is_login:
            self._repositories["corp_struct_item"] = CorpStructItemRepository(
                corp_struct_items=list(self._api.corp_struct_items()),
            )

        return (
            self._repositories["corp_struct_item"]
            if "corp_struct_item" in self._repositories
            else CorpStructItemRepository([])
        )

    def repositoryEmployeePosition(self, reload: bool = False) -> EmployeePositionRepository:
        if ("employee_position" not in self._repositories or reload) and self._is_login:
            self._repositories["employee_position"] = EmployeePositionRepository(
                employee_positions=list(self._api.employees_positions()),
            )

        return (
            self._repositories["employee_position"]
            if "employee_position" in self._repositories
            else EmployeePositionRepository([])
        )

    def repositoryProviders(self, reload: bool = False) -> ProvidersRepository:
        if ("providers" not in self._repositories or reload) and self._is_login:
            clients, projects = self._api.providers()
            self._repositories["providers"] = ProvidersRepository(
                clients=list(clients),
                projects=list(projects),
            )

        return self._repositories["providers"] if "providers" in self._repositories else ProvidersRepository([], [])

    def time_record_save(self, time_records: list[TimeRecord]) -> list[TimeRecord]:
        return list(self._api.time_record_save(time_records=time_records))
