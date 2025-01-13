import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    alias: str
    deleted: bool
    id: int
    name: str
    salary_coefficient: int


@dataclass(frozen=True)
class CategoryBinding:
    category_id: int
    corp_struct_item_id: int
    id: int
    position_id: int
    role_id: int


@dataclass(frozen=True)
class CorpStructItem:
    alias: str
    id: int
    name: str


@dataclass(frozen=True)
class Client:
    id: int
    name: str


@dataclass(frozen=True)
class Employee:
    email: str
    first_name: str
    id: int
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class EmployeePosition:
    acting: bool
    alias: str
    corp_struct_item_alias: str
    corp_struct_item_id: int
    employee_id: int
    id: int
    position_id: int


@dataclass(frozen=True)
class Project:
    active: bool
    id: int
    name: str


@dataclass(frozen=True)
class Report:
    date: datetime.date
    employee_id: int
    have_problems: bool
    no_tasks: bool
    problems: str
    tasks: list["TimeRecord"]
    id: int | None = None

    @property
    def next_time_record_order_number(self) -> int:
        return max((time_record.order_number for time_record in self.tasks), default=0) + 1


@dataclass(frozen=True)
class TimeRecord:
    category_id: int
    client_id: int
    corp_struct_item_id: int
    description: str
    hours: float
    invoice_hours: int
    order_number: int
    project_id: int
    report_id: int
    salary_coefficient: int
    salary_coefficient_type: int
    id: int | None = None
    override_employee_id: int | None = None
