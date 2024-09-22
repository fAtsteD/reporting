from reporting.models.report import Report
from reporting.services.reporting.api import ReportingApi


class ReportingException(Exception):
    pass


def send_tasks(report: Report) -> None:
    reporting = ReportingApi()

    # TODO: reporting requires prerequest, because it has cookie variable for session and all requests before setting cookie is useless
    if not reporting.init():
        raise ReportingException(reporting.last_error)
    if not reporting.login():
        raise ReportingException(reporting.last_error)
    if not reporting.init():
        raise ReportingException(reporting.last_error)
    if not reporting.load_categories():
        raise ReportingException(reporting.last_error)
    if not reporting.load_corp_struct_items():
        raise ReportingException(reporting.last_error)
    if not reporting.load_projects():
        raise ReportingException(reporting.last_error)
    if not reporting.load_positions():
        raise ReportingException(reporting.last_error)

    reporting_reports = reporting.get_reports(report.date)
    if reporting_reports is None:
        raise ReportingException(reporting.last_error)

    reporting_report_id = None
    if len(reporting_reports) > 0:
        reporting_report_id = reporting_reports[0].get_id()

    reporting_report = reporting.set_report(report.date, reporting_report_id)
    if reporting_report is None:
        raise ReportingException(reporting.last_error)

    for task in report.tasks:
        if reporting.add_task(task, reporting_report):
            print(f"[+] {task}")
        else:
            print(f"[-] {task}")

    print()
    reporting.logout()
