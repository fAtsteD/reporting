from dataclasses import dataclass
from typing import Iterable

from reporting.qatestlab_portal.reporting.models import (
    Category,
    CategoryBinding,
    Client,
    CorpStructItem,
    EmployeePosition,
    Project,
)


@dataclass
class CategoryRepository:
    categories: list[Category]
    categories_binding: list[CategoryBinding]

    def get_by_name_and_corp_struct_item(self, name: str, corp_struct_item_id: int) -> Category | None:
        allowed_category_ids = list(map(
            lambda category_binding: category_binding.category_id,
            filter(
                lambda category_binding: category_binding.corp_struct_item_id == corp_struct_item_id,
                self.categories_binding,
            ),
        ))
        categories = filter(lambda category: category.id in allowed_category_ids, self.categories)

        for category in categories:
            if category.name == name:
                return category

        return None


@dataclass
class CorpStructItemRepository:
    corp_struct_items: list[CorpStructItem]

    def get_by_id(self, id: int) -> CorpStructItem | None:
        for corp_struct_item in self.corp_struct_items:
            if corp_struct_item.id == id:
                return corp_struct_item

        return None

    def get_by_alias(self, alias: str) -> CorpStructItem | None:
        for corp_struct_item in self.corp_struct_items:
            if corp_struct_item.alias == alias:
                return corp_struct_item

        return None


@dataclass
class EmployeePositionRepository:
    employee_positions: list[EmployeePosition]

    def get_by_employee_id(self, employee_id: int) -> Iterable[EmployeePosition]:
        return filter(lambda employee_position: employee_position.employee_id == employee_id, self.employee_positions)

    def get_main_position_by_employee_id(self, employee_id: int) -> EmployeePosition | None:
        employee_positions = list(
            filter(lambda employee_position: not employee_position.acting, self.get_by_employee_id(employee_id))
        )
        return employee_positions.pop() if len(employee_positions) else None


@dataclass
class ProvidersRepository:
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
