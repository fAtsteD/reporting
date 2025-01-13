import reporting.qatestlab_portal.reporting.models as reporting_models
from reporting import config
from reporting.models import Report
from reporting.qatestlab_portal.reporting.client import ReportingClient


def send_tasks(report: Report) -> None:
    reporting_client = ReportingClient(config.reporting.url)
    reporting_client.login(config.reporting.login, config.reporting.password)

    if reporting_client.employee is None:
        raise Exception("Failed to get employee")

    portal_reports = reporting_client.reports(report.date)
    portal_report = reporting_client.report_save(
        reporting_models.Report(
            date=report.date,
            employee_id=reporting_client.employee.id,
            have_problems=False,
            id=portal_reports[0].id if len(portal_reports) else None,
            no_tasks=True,
            problems="",
            timeRecords=[],
        )
    )

    if not portal_report or not portal_report.id:
        raise Exception("Failed create/load report")

    time_record_index = portal_report.next_time_record_order_number
    time_records: list[reporting_models.TimeRecord] = []
    employee_position = reporting_client.repositoryEmployeePosition().get_main_position_by_employee_id(
        reporting_client.employee.id
    )

    if not employee_position:
        raise Exception("Employee does not have a main position")

    for task in report.tasks:
        corp_struct_item = reporting_client.repositoryCorpStructItem().get_by_id(employee_position.corp_struct_item_id)

        if task.project.alias in config.reporting.project_to_corp_struct_item.keys():
            corp_struct_item_alias = config.reporting.project_to_corp_struct_item[task.project.alias]
            corp_struct_item = reporting_client.repositoryCorpStructItem().get_by_alias(corp_struct_item_alias)

        if not corp_struct_item:
            print(f"[-] {task}")
            print(f"  Corp struct item not found")
            continue

        category_name = task.kind.name

        if task.kind.alias in config.reporting.kinds.keys():
            category_name = config.reporting.kinds[task.kind.alias]

        category = reporting_client.repositoryCategory().get_by_name_and_corp_struct_item(
            category_name, corp_struct_item.id
        )

        if not category or category.deleted:
            print(f"[-] {task}")
            print(f"  Category not found for {task.kind.name}")
            continue

        project_name = task.project.name

        if task.project.alias in config.reporting.projects.keys():
            project_name = config.reporting.projects[task.project.alias]

        project = reporting_client.repositoryProviders().get_project_by_name(project_name)

        if not project or not project.active:
            print(f"[-] {task}")
            print(f"  Project not found for {task.project.name}")
            continue

        time_records.append(
            reporting_models.TimeRecord(
                category_id=category.id,
                client_id=None,
                corp_struct_item_id=corp_struct_item.id,
                description=task.summary,
                hours=round(task.logged_rounded / 60 / 60 * 100),
                invoice_hours=0,
                order_number=time_record_index,
                project_id=project.id,
                report_id=portal_report.id,
                salary_coefficient=category.salary_coefficient,
                salary_coefficient_type=0,
            )
        )
        time_record_index += 1
        print(f"[+] {task}")

    reporting_client.time_record_save(time_records)
