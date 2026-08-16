import datetime
from types import TracebackType
from typing import Any, Self

from reporting.qatestlab_portal.base import BaseApi
from reporting.qatestlab_portal.exceptions import PortalNotAuthorizedException
from reporting.qatestlab_portal.models import (
    Category,
    CategoryBinding,
    CategoryCollection,
    Client,
    CorpStructItem,
    CorpStructItemCollection,
    Employee,
    EmployeePosition,
    EmployeePositionCollection,
    Project,
    ProviderCollection,
    Report,
    TimeRecord,
)


class QATestLabPortal(BaseApi):
    def __init__(self, base_url: str, request_session: Any = None) -> None:
        super().__init__(base_url=base_url, request_session=request_session)
        self._employee: Employee | None = None
        self._is_authorized = False
        self._category_collection: CategoryCollection | None = None
        self._corp_struct_item_collection: CorpStructItemCollection | None = None
        self._employee_position_collection: EmployeePositionCollection | None = None
        self._provider_collection: ProviderCollection | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.logout()

    @property
    def employee(self) -> Employee:
        self._ensure_authorized()

        if self._employee is None:
            self._employee = self.init()

        return self._employee

    @property
    def category_collection(self) -> CategoryCollection:
        self._ensure_authorized()

        if self._category_collection is None:
            self._category_collection = CategoryCollection(
                categories=list(self.categories()),
                categories_binding=list(self.categories_bindings()),
            )

        return self._category_collection

    @property
    def corp_struct_item_collection(self) -> CorpStructItemCollection:
        self._ensure_authorized()

        if self._corp_struct_item_collection is None:
            self._corp_struct_item_collection = CorpStructItemCollection(
                corp_struct_items=list(self.corp_struct_items()),
            )

        return self._corp_struct_item_collection

    @property
    def employee_position_collection(self) -> EmployeePositionCollection:
        self._ensure_authorized()

        if self._employee_position_collection is None:
            self._employee_position_collection = EmployeePositionCollection(
                employee_positions=list(self.employees_positions()),
            )

        return self._employee_position_collection

    @property
    def provider_collection(self) -> ProviderCollection:
        self._ensure_authorized()

        if self._provider_collection is None:
            clients, projects = self.providers()
            self._provider_collection = ProviderCollection(
                clients=list(clients),
                projects=list(projects),
            )

        return self._provider_collection

    def login(self, login: str, password: str) -> None:
        self._post("common/login", data={"login": login, "password": password})
        self._is_authorized = True

    def logout(self) -> None:
        if not self._is_authorized:
            return

        self._post("common/logout")
        self._is_authorized = False
        self._employee = None
        self._category_collection = None
        self._corp_struct_item_collection = None
        self._employee_position_collection = None
        self._provider_collection = None

    def categories(self) -> list[Category]:
        self._ensure_authorized()

        return [Category.model_validate(category) for category in self._get("common/categories")]

    def categories_bindings(self) -> list[CategoryBinding]:
        self._ensure_authorized()

        return [CategoryBinding.model_validate(category_binding) for category_binding in self._get("category-binding")]

    def corp_struct_items(self) -> list[CorpStructItem]:
        self._ensure_authorized()

        return [CorpStructItem.model_validate(item) for item in self._get("corp-struct-items")]

    def employees_positions(self) -> list[EmployeePosition]:
        self._ensure_authorized()

        return [EmployeePosition.model_validate(item) for item in self._get("employees/positions")]

    def init(self) -> Employee:
        self._ensure_authorized()

        return Employee.from_init(self._get("common/init"))

    def providers(self) -> tuple[list[Client], list[Project]]:
        self._ensure_authorized()
        response_data = self._get("providers")

        return (
            [Client.model_validate(client) for client in response_data["clients"]],
            [Project.model_validate(project) for project in response_data["projects"]],
        )

    def reports(self, date: datetime.date) -> list[Report]:
        self._ensure_authorized()
        response_data = self._get(
            "report",
            params={
                "date": date.strftime("%Y-%m-%d"),
                "employeeId": self.employee.id,
            },
        )

        return [Report.model_validate(report) for report in response_data]

    def report_save(self, report: Report) -> Report:
        self._ensure_authorized()
        response_data = self._put(
            "report",
            data=report.model_dump(by_alias=True, exclude={"time_records"}, mode="json"),
        )
        saved_report = Report.model_validate(response_data)
        saved_report.time_records = report.time_records

        return saved_report

    def time_record_save(self, time_records: list[TimeRecord]) -> list[TimeRecord]:
        self._ensure_authorized()
        response_data = self._post(
            "time-records",
            data=[time_record.model_dump(by_alias=True, exclude={"id"}, mode="json") for time_record in time_records],
        )

        return [TimeRecord.model_validate(time_record) for time_record in response_data]

    def _ensure_authorized(self) -> None:
        if not self._is_authorized:
            raise PortalNotAuthorizedException("Portal client is not authorized. Call login() first.")
