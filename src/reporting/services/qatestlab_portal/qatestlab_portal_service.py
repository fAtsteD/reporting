from reporting import config
from reporting.database.models import Report, Task
from reporting.qatestlab_portal.client import QATestLabPortal
from reporting.qatestlab_portal.models import Report as PortalReport
from reporting.qatestlab_portal.models import TimeRecord
from reporting.services.qatestlab_portal.exceptions import (
    QATestLabPortalError,
    QATestLabPortalNotConfiguredError,
)
from reporting.services.qatestlab_portal.models import PortalTaskResult, PortalTaskStatus

PORTAL_HOURS_SCALE = 100


def convert_seconds_to_portal_hours(seconds: int) -> int:
    return round(seconds / 60 / 60 * PORTAL_HOURS_SCALE)


def send_tasks(report: Report) -> list[PortalTaskResult]:
    if not config.qatestlab_portal.is_use:
        raise QATestLabPortalNotConfiguredError(
            "QATestLab Portal is not configured. Api url, login and password are required"
        )

    with QATestLabPortal(config.qatestlab_portal.url) as portal:
        portal.login(config.qatestlab_portal.login, config.qatestlab_portal.password)

        return _send_report_tasks(portal, report)


def _failed(task: Task, reason: str) -> PortalTaskResult:
    return PortalTaskResult(status=PortalTaskStatus.FAILED, task=task, reason=reason)


def _send_report_tasks(portal: QATestLabPortal, report: Report) -> list[PortalTaskResult]:
    portal_reports = portal.reports(report.date)
    portal_report = portal.report_save(
        PortalReport(
            date=report.date,
            employeeId=portal.employee.id,
            haveProblems=False,
            id=portal_reports[0].id if len(portal_reports) else None,
            noTasks=False,
            problems="",
            timeRecords=[],
        )
    )

    if not portal_report or not portal_report.id:
        raise QATestLabPortalError("Failed create/load report")

    time_record_index = portal_report.next_time_record_order_number
    time_records: list[TimeRecord] = []
    results: list[PortalTaskResult] = []
    employee_position = portal.employee_position_collection.get_main_position_by_employee_id(portal.employee.id)

    if not employee_position:
        raise QATestLabPortalError("Employee does not have a main position")

    for task in report.tasks:
        corp_struct_item = portal.corp_struct_item_collection.get_by_id(employee_position.corp_struct_item_id)

        if task.project.alias in config.qatestlab_portal.project_to_corp_struct_item:
            corp_struct_item_alias = config.qatestlab_portal.project_to_corp_struct_item[task.project.alias]
            corp_struct_item = portal.corp_struct_item_collection.get_by_alias(corp_struct_item_alias)

        if not corp_struct_item:
            results.append(_failed(task, "Corp struct item not found"))
            continue

        category_name = config.qatestlab_portal.kinds.get(task.kind.alias, task.kind.name)
        category = portal.category_collection.get_by_name_and_corp_struct_item(category_name, corp_struct_item.id)

        if not category or category.deleted:
            results.append(_failed(task, f"Category not found for {task.kind.name}"))
            continue

        project_name = config.qatestlab_portal.projects.get(task.project.alias, task.project.name)
        project = portal.provider_collection.get_project_by_name(project_name)

        if not project or not project.active:
            results.append(_failed(task, f"Project not found for {task.project.name}"))
            continue

        time_records.append(
            TimeRecord(
                categoryId=category.id,
                clientId=None,
                corpStructItemId=corp_struct_item.id,
                description=task.summary,
                hours=convert_seconds_to_portal_hours(task.logged_rounded),
                invoiceHours=0,
                orderNumber=time_record_index,
                projectId=project.id,
                reportId=portal_report.id,
                salaryCoefficient=category.salary_coefficient,
                salaryCoefficientType=0,
            )
        )
        time_record_index += 1
        results.append(PortalTaskResult(status=PortalTaskStatus.SENT, task=task))

    portal.time_record_save(time_records)

    return results
