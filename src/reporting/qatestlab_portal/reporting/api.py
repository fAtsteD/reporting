import datetime
from typing import Iterable

from requests.sessions import Session

from reporting.qatestlab_portal.reporting import PortalRequestException
from reporting.qatestlab_portal.reporting.models import (
    Category,
    CategoryBinding,
    Client,
    CorpStructItem,
    Employee,
    EmployeePosition,
    Project,
    Report,
    TimeRecord,
)


class ReportingApi:
    def __init__(self, base_url: str, request_session: Session = Session()) -> None:
        self.base_url = base_url.rstrip("/")
        self.base_url += "/reporting/api" if not self.base_url.endswith("reporting/api") else ""
        self._request_session = request_session

        self.ping()

    def categories(self) -> Iterable[Category]:
        response_data = self._request(
            endpoint="common/categories",
            method="get",
        )
        return map(
            lambda category: Category(
                alias=category["alias"],
                deleted=category["deleted"],
                name=category["name"],
                id=category["id"],
                salary_coefficient=category["salaryCoefficient"],
            ),
            response_data,
        )

    def categories_bindings(self) -> Iterable[CategoryBinding]:
        response_data = self._request(
            endpoint="category-binding",
            method="get",
        )
        return map(
            lambda category_binding: CategoryBinding(
                category_id=category_binding["categoryId"],
                corp_struct_item_id=category_binding["corpStructItemId"],
                id=category_binding["id"],
                position_id=category_binding["positionId"],
                role_id=category_binding["roleId"],
            ),
            response_data,
        )

    def corp_struct_items(self) -> Iterable[CorpStructItem]:
        response_data = self._request(
            endpoint="corp-struct-items",
            method="get",
        )
        return map(
            lambda corp_struct_item: CorpStructItem(
                alias=corp_struct_item["alias"],
                name=corp_struct_item["name"],
                id=corp_struct_item["id"],
            ),
            response_data,
        )

    def employees_positions(self) -> Iterable[EmployeePosition]:
        response_data = self._request(
            endpoint="employees/positions",
            method="get",
        )
        return map(
            lambda employee_position: EmployeePosition(
                acting=employee_position["acting"],
                alias=employee_position["alias"],
                corp_struct_item_alias=employee_position["corpStructItemAlias"],
                corp_struct_item_id=employee_position["corpStructItemId"],
                employee_id=employee_position["employeeId"],
                id=employee_position["id"],
                position_id=employee_position["positionId"],
            ),
            response_data,
        )

    def init(self) -> Employee | None:
        response_data = self._request(
            endpoint="common/init",
            method="get",
        )
        return Employee(
            email=response_data["currentUser"]["user"]["email"],
            first_name=response_data["currentUser"]["user"]["firstName"],
            id=response_data["currentUser"]["user"]["employeeId"],
            last_name=response_data["currentUser"]["user"]["lastName"],
        )

    def login(self, login: str, password: str) -> bool:
        data = {"login": login, "password": password}
        response = self._request_session.post(f"{self.base_url}/common/login", json=data)

        if response.status_code >= 500:
            raise PortalRequestException(
                f"Portal reporting API login has bad status code: {response.status_code}",
                response=response,
            )

        if response.status_code < 400:
            return True

        try:
            response_data = response.json()
        except Exception:
            raise PortalRequestException(f"Portal reporting API login has bad body", response=response)

        if "errorMessage" in response_data:
            raise PortalRequestException(
                f"Portal reporting API login has error: {response_data['errorMessage']}",
                response=response,
            )

        return False

    def logout(self) -> None:
        response = self._request_session.post(f"{self.base_url}/common/logout")

        if response.status_code >= 500:
            raise PortalRequestException(
                f"Portal reporting API logout has bad status code: {response.status_code}",
                response=response,
            )

        if response.status_code < 400:
            return

        try:
            response_data = response.json()
        except Exception:
            raise PortalRequestException(f"Portal reporting API logout has bad body", response=response)

        if "errorMessage" in response_data:
            raise PortalRequestException(
                f"Portal reporting API logout has error: {response_data['errorMessage']}",
                response=response,
            )

    def ping(self) -> None:
        """
        Check portal availability, initialize session
        """
        response = self._request_session.get(f"{self.base_url}/ping")

        if response.status_code >= 500:
            raise PortalRequestException("Portal reporting API is not available", response=response)

    def providers(self) -> tuple[Iterable[Client], Iterable[Project]]:
        response_data = self._request(
            endpoint="providers",
            method="get",
        )
        return (
            map(
                lambda client: Client(
                    id=client["id"],
                    name=client["name"],
                ),
                response_data["clients"],
            ),
            map(
                lambda project: Project(
                    active=project["active"],
                    id=project["id"],
                    name=project["name"],
                ),
                response_data["projects"],
            ),
        )

    def reports(self, date: datetime.date, employee_id: int) -> Iterable[Report]:
        response_data = self._request(
            endpoint="report",
            method="get",
            params={
                "date": date.strftime("%Y-%m-%d"),
                "employeeId": employee_id,
            },
        )
        return map(
            lambda report: Report(
                date=report["date"],
                employee_id=report["employeeId"],
                have_problems=report.get("haveProblems"),
                id=report["id"],
                no_tasks=report["noTasks"],
                problems=report["problems"],
                tasks=list(
                    map(
                        lambda task: TimeRecord(
                            category_id=task["categoryId"],
                            client_id=task["clientId"],
                            corp_struct_item_id=task["corpStructItemId"],
                            description=task["description"],
                            hours=task["hours"],
                            id=task["id"],
                            invoice_hours=task["invoiceHours"],
                            order_number=task["orderNumber"],
                            project_id=task["projectId"],
                            report_id=task["reportId"],
                            salary_coefficient=task["salaryCoefficient"],
                            salary_coefficient_type=task["salaryCoefficientType"],
                        ),
                        report["tasks"],
                    )
                ),
            ),
            response_data,
        )

    def report_save(self, report: Report) -> Report:
        response_data = self._request(
            data={
                "date": report.date.strftime("%Y-%m-%d"),
                "employeeId": report.employee_id,
                "haveProblems": report.have_problems,
                "id": report.id,
                "noTasks": report.no_tasks,
                "problems": report.problems,
            },
            endpoint="report",
            method="put",
        )
        return Report(
            date=response_data["date"],
            employee_id=response_data["employeeId"],
            have_problems=response_data["haveProblems"],
            id=response_data["id"],
            no_tasks=response_data["noTasks"],
            problems=response_data["problems"],
            tasks=report.tasks,
        )

    def time_record_save(self, time_records: Iterable[TimeRecord]) -> Iterable[TimeRecord]:
        response_data = self._request(
            data=list(
                map(
                    lambda time_record: {
                        "categoryId": time_record.category_id,
                        "clientId": time_record.client_id,
                        "corpStructItemId": time_record.corp_struct_item_id,
                        "description": time_record.description,
                        "hours": time_record.hours,
                        "invoiceHours": time_record.invoice_hours,
                        "orderNumber": time_record.order_number,
                        "projectId": time_record.project_id,
                        "reportId": time_record.report_id,
                        "salaryCoefficient": time_record.salary_coefficient,
                        "salaryCoefficientType": time_record.salary_coefficient_type,
                    },
                    time_records,
                )
            ),
            endpoint="time-records",
            method="post",
        )
        return map(
            lambda time_record: TimeRecord(
                category_id=time_record["categoryId"],
                client_id=time_record["clientId"],
                corp_struct_item_id=time_record["corpStructItemId"],
                description=time_record["description"],
                hours=time_record["hours"],
                id=time_record["id"],
                invoice_hours=time_record["invoiceHours"],
                order_number=time_record["orderNumber"],
                project_id=time_record["projectId"],
                report_id=time_record["reportId"],
                salary_coefficient=time_record["salaryCoefficient"],
                salary_coefficient_type=time_record["salaryCoefficientType"],
            ),
            response_data,
        )

    def _request(self, method: str, endpoint: str, params: dict | None = None, data: list | dict | None = None) -> dict:
        endpoint = endpoint.strip("/")
        response = self._request_session.request(
            json=data,
            method=method,
            params=params,
            url=f"{self.base_url}/{endpoint}",
        )

        if response.status_code >= 400:
            raise PortalRequestException(
                f"Portal reporting API {endpoint} has bad status code: {response.status_code}",
                response=response,
            )

        try:
            response_data = response.json()
        except Exception:
            raise PortalRequestException(f"Portal reporting API {endpoint} has bad body", response=response)

        if "errorMessage" in response_data:
            raise PortalRequestException(
                f"Portal reporting API {endpoint} has error: {response_data['errorMessage']}",
                response=response,
            )

        return response_data
