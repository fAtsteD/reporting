from reporting import config
from reporting.database.models import Report
from reporting.qatestlab_portal.client import QATestLabPortal
from reporting.qatestlab_portal.models import Report as PortalReport
from reporting.qatestlab_portal.models import TimeRecord
from reporting.services.qatestlab_portal.exceptions import QATestLabPortalError


def send_tasks(report: Report) -> None:
    with QATestLabPortal(config.qatestlab_portal.url) as portal:
        portal.login(config.qatestlab_portal.login, config.qatestlab_portal.password)
        _send_report_tasks(portal, report)


def _send_report_tasks(portal: QATestLabPortal, report: Report) -> None:
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
    employee_position = portal.employee_position_collection.get_main_position_by_employee_id(portal.employee.id)

    if not employee_position:
        raise QATestLabPortalError("Employee does not have a main position")

    for task in report.tasks:
        corp_struct_item = portal.corp_struct_item_collection.get_by_id(employee_position.corp_struct_item_id)

        if task.project.alias in config.qatestlab_portal.project_to_corp_struct_item:
            corp_struct_item_alias = config.qatestlab_portal.project_to_corp_struct_item[task.project.alias]
            corp_struct_item = portal.corp_struct_item_collection.get_by_alias(corp_struct_item_alias)

        if not corp_struct_item:
            print(f"[-] {task}")
            print("  Corp struct item not found")
            continue

        category_name = task.kind.name

        if task.kind.alias in config.qatestlab_portal.kinds:
            category_name = config.qatestlab_portal.kinds[task.kind.alias]

        category = portal.category_collection.get_by_name_and_corp_struct_item(category_name, corp_struct_item.id)

        if not category or category.deleted:
            print(f"[-] {task}")
            print(f"  Category not found for {task.kind.name}")
            continue

        project_name = task.project.name

        if task.project.alias in config.qatestlab_portal.projects:
            project_name = config.qatestlab_portal.projects[task.project.alias]

        project = portal.provider_collection.get_project_by_name(project_name)

        if not project or not project.active:
            print(f"[-] {task}")
            print(f"  Project not found for {task.project.name}")
            continue

        time_records.append(
            TimeRecord(
                categoryId=category.id,
                clientId=None,
                corpStructItemId=corp_struct_item.id,
                description=task.summary,
                hours=round(task.logged_rounded / 60 / 60 * 100),
                invoiceHours=0,
                orderNumber=time_record_index,
                projectId=project.id,
                reportId=portal_report.id,
                salaryCoefficient=category.salary_coefficient,
                salaryCoefficientType=0,
            )
        )
        time_record_index += 1
        print(f"[+] {task}")

    portal.time_record_save(time_records)
