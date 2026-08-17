import datetime
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PortalBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class Category(PortalBaseModel):
    alias: str
    deleted: bool
    id: int
    name: str
    salary_coefficient: int = Field(alias="salaryCoefficient")


class CategoryBinding(PortalBaseModel):
    category_id: int = Field(alias="categoryId")
    corp_struct_item_id: int | None = Field(alias="corpStructItemId")
    id: int
    position_id: int | None = Field(alias="positionId")
    role_id: int | None = Field(alias="roleId")


class CategoryCollection(PortalBaseModel):
    categories: list[Category]
    categories_binding: list[CategoryBinding]

    def get_by_name_and_corp_struct_item(self, name: str, corp_struct_item_id: int) -> Category | None:
        allowed_category_ids = [
            category_binding.category_id
            for category_binding in self.categories_binding
            if category_binding.corp_struct_item_id == corp_struct_item_id
        ]

        for category in self.categories:
            if category.id in allowed_category_ids and category.name == name:
                return category

        return None


class Client(PortalBaseModel):
    id: int
    name: str


class CorpStructItem(PortalBaseModel):
    alias: str
    id: int
    name: str


class CorpStructItemCollection(PortalBaseModel):
    corp_struct_items: list[CorpStructItem]

    def get_by_alias(self, alias: str) -> CorpStructItem | None:
        for corp_struct_item in self.corp_struct_items:
            if corp_struct_item.alias == alias:
                return corp_struct_item

        return None

    def get_by_id(self, id: int) -> CorpStructItem | None:
        for corp_struct_item in self.corp_struct_items:
            if corp_struct_item.id == id:
                return corp_struct_item

        return None


class Employee(PortalBaseModel):
    email: str
    first_name: str = Field(alias="firstName")
    id: int
    last_name: str = Field(alias="lastName")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_init(cls, data: dict[str, Any]) -> "Employee":
        user = data["currentUser"]["user"]

        return cls(
            email=user["email"],
            firstName=user["firstName"],
            id=user["employeeId"],
            lastName=user["lastName"],
        )


class EmployeePosition(PortalBaseModel):
    acting: bool
    alias: str
    corp_struct_item_alias: str = Field(alias="corpStructItemAlias")
    corp_struct_item_id: int = Field(alias="corpStructItemId")
    employee_id: int | None = Field(alias="employeeId")
    id: int
    position_id: int = Field(alias="positionId")


class EmployeePositionCollection(PortalBaseModel):
    employee_positions: list[EmployeePosition]

    def get_by_employee_id(self, employee_id: int) -> Iterable[EmployeePosition]:
        return (
            employee_position
            for employee_position in self.employee_positions
            if employee_position.employee_id == employee_id
        )

    def get_main_position_by_employee_id(self, employee_id: int) -> EmployeePosition | None:
        employee_positions = [
            employee_position
            for employee_position in self.get_by_employee_id(employee_id)
            if not employee_position.acting
        ]

        return employee_positions.pop() if len(employee_positions) else None


class Project(PortalBaseModel):
    active: bool
    id: int
    name: str


class ProviderCollection(PortalBaseModel):
    clients: list[Client]
    projects: list[Project]

    def get_client_by_name(self, name: str) -> Client | None:
        for client in self.clients:
            if client.name == name:
                return client

        return None

    def get_project_by_name(self, name: str) -> Project | None:
        for project in self.projects:
            if project.name == name:
                return project

        return None


class TimeRecord(PortalBaseModel):
    category_id: int = Field(alias="categoryId")
    client_id: int | None = Field(alias="clientId")
    corp_struct_item_id: int = Field(alias="corpStructItemId")
    description: str
    hours: float
    invoice_hours: int = Field(alias="invoiceHours")
    order_number: int = Field(alias="orderNumber")
    project_id: int | None = Field(alias="projectId")
    report_id: int = Field(alias="reportId")
    salary_coefficient: int = Field(alias="salaryCoefficient")
    salary_coefficient_type: int = Field(alias="salaryCoefficientType")
    id: int | None = None
    override_employee_id: int | None = Field(default=None, alias="overrideEmployeeId")


class Report(PortalBaseModel):
    date: datetime.date
    employee_id: int = Field(alias="employeeId")
    have_problems: bool | None = Field(alias="haveProblems")
    no_tasks: bool = Field(alias="noTasks")
    problems: str | None
    time_records: list[TimeRecord] = Field(default_factory=list, alias="timeRecords")
    id: int | None = None

    @property
    def next_time_record_order_number(self) -> int:
        return max((time_record.order_number for time_record in self.time_records), default=0) + 1
